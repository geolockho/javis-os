"""Nghiệp vụ: tạo request, duyệt, tạo link, tải kubeconfig, revoke.

Mọi kiểm tra quyền làm ở đây (phía server), không tin dữ liệu form.
"""
from __future__ import annotations

import hashlib
import logging
import re
import secrets
from dataclasses import dataclass
from datetime import timedelta

import psycopg

from . import slack
from .auth import Identity
from .config import Settings, format_duration
from .db import Database
from .catalog import NamespaceCatalog, namespace_forbidden
from .k8s import ClusterError, ClusterOps
from .kubeconfig import build_kubeconfig, kubeconfig_filename

log = logging.getLogger(__name__)

ACTIVE_STATUSES = ("pending", "approved", "issuing", "issued")
_LINK_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")
# Lệch quá 60 giây so với thời hạn đã xin thì coi là API server đã cắt ngắn
TRUNCATION_TOLERANCE_SECONDS = 60


class ServiceError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass
class Download:
    filename: str
    content: str
    sa_name: str
    expires_at: object
    truncated: bool


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Service:
    def __init__(self, settings: Settings, db: Database, clusters: dict[str, ClusterOps],
                 catalog: NamespaceCatalog):
        self.settings = settings
        self.db = db
        self.clusters = clusters
        self.catalog = catalog

    # ------------------------------------------------------------------ audit
    @staticmethod
    def _audit(conn, actor: str, action: str, result: str, req: dict | None = None, **extra) -> None:
        req = req or {}
        conn.execute(
            """INSERT INTO audit_log (actor, action, result, request_id, requester_email, cluster, namespace,
                                      role, approver, downloaded_at, token_expires_at, detail)
               VALUES (%(actor)s, %(action)s, %(result)s, %(request_id)s, %(requester_email)s, %(cluster)s,
                       %(namespace)s, %(role)s, %(approver)s, %(downloaded_at)s, %(token_expires_at)s, %(detail)s)""",
            {
                "actor": actor,
                "action": action,
                "result": result,
                "request_id": extra.get("request_id", req.get("id")),
                "requester_email": extra.get("requester_email", req.get("requester_email")),
                "cluster": extra.get("cluster", req.get("cluster")),
                "namespace": extra.get("namespace", req.get("namespace")),
                "role": extra.get("role", req.get("role")),
                "approver": extra.get("approver", req.get("decided_by")),
                "downloaded_at": extra.get("downloaded_at", req.get("issued_at")),
                "token_expires_at": extra.get("token_expires_at", req.get("token_expires_at")),
                "detail": extra.get("detail"),
            },
        )

    def _audit_tx(self, *args, **kwargs) -> None:
        try:
            with self.db.tx() as conn:
                self._audit(conn, *args, **kwargs)
        except Exception:  # noqa: BLE001
            log.exception("Ghi audit lỗi")

    # ------------------------------------------------------------------ dev
    def form_options(self, identity: Identity) -> dict[str, list[str]]:
        # Mọi người đăng nhập thấy cùng một danh mục, không lọc theo group
        out: dict[str, list[str]] = {}
        for g in self.catalog.grants():
            if g.cluster in self.clusters:
                out.setdefault(g.cluster, []).append(g.namespace)
        return out

    def create_request(self, identity: Identity, cluster: str, namespace: str, expiration_seconds: int) -> int:
        namespace = (namespace or "").strip().lower()
        cluster = (cluster or "").strip()
        target = {"cluster": cluster, "namespace": namespace, "requester_email": identity.email}

        if cluster not in self.clusters:
            raise ServiceError(400, "Cluster không hợp lệ")
        if namespace_forbidden(namespace, self.settings):
            self._audit_tx(identity.email, "request_created", "denied", target, detail="namespace bị cấm")
            raise ServiceError(403, "Namespace này không được cấp")
        grant = self.catalog.find(cluster, namespace)
        if grant is None:
            self._audit_tx(identity.email, "request_created", "denied", target,
                           detail="namespace chưa mở (không có label kubeconfig-generator/enabled=true)")
            raise ServiceError(403, "Namespace này chưa được mở cho xin quyền")
        if grant.role not in self.settings.allowed_cluster_roles:
            raise ServiceError(403, "Role không được phép")
        if expiration_seconds not in self.settings.expiration_options:
            raise ServiceError(400, "Thời hạn không hợp lệ")

        try:
            if not self.clusters[cluster].namespace_exists(namespace):
                raise ServiceError(400, "Namespace không tồn tại trên cluster")
        except ClusterError as exc:
            # Không chặn tạo request vì lỗi mạng tạm thời; lúc tải sẽ kiểm lại
            log.warning("Không kiểm tra được namespace %s/%s: %s", cluster, namespace, exc)

        try:
            with self.db.tx() as conn:
                # Khoá theo email để đếm request chờ duyệt không bị đua
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (identity.email,))
                pending = conn.execute(
                    "SELECT count(*) AS n FROM access_request WHERE requester_email=%s AND status='pending'",
                    (identity.email,),
                ).fetchone()["n"]
                if pending >= self.settings.max_pending_per_user:
                    raise ServiceError(429, f"Bạn đã có {pending} request chờ duyệt (tối đa "
                                            f"{self.settings.max_pending_per_user})")
                dup = conn.execute(
                    "SELECT id, status FROM access_request WHERE requester_email=%s AND cluster=%s"
                    " AND namespace=%s AND status = ANY(%s)",
                    (identity.email, cluster, namespace, list(ACTIVE_STATUSES)),
                ).fetchone()
                if dup:
                    raise ServiceError(409, f"Đã có request #{dup['id']} ({dup['status']}) cho namespace này")
                req = conn.execute(
                    """INSERT INTO access_request (requester_email, cluster, namespace, role, requested_seconds)
                       VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                    (identity.email, cluster, namespace, grant.role, expiration_seconds),
                ).fetchone()
                self._audit(conn, identity.email, "request_created", "ok", req,
                            detail=f"thời hạn xin {format_duration(expiration_seconds)}")
        except psycopg.errors.UniqueViolation:
            raise ServiceError(409, "Đã có request còn hiệu lực cho namespace này") from None

        slack.notify(
            self.settings.slack_webhook_url,
            f":key: Request kubeconfig mới #{req['id']}: {identity.email} xin `{grant.role}` ở "
            f"`{cluster}/{namespace}` trong {format_duration(expiration_seconds)}. "
            f"Duyệt tại {self.settings.public_url}/admin",
        )
        return req["id"]

    def my_requests(self, email: str, limit: int = 50) -> list[dict]:
        with self.db.tx() as conn:
            return conn.execute(
                "SELECT * FROM access_request WHERE requester_email=%s ORDER BY id DESC LIMIT %s",
                (email, limit),
            ).fetchall()

    def cancel_request(self, identity: Identity, request_id: int) -> None:
        with self.db.tx() as conn:
            req = conn.execute(
                "UPDATE access_request SET status='cancelled', updated_at=now()"
                " WHERE id=%s AND requester_email=%s AND status IN ('pending','approved') RETURNING *",
                (request_id, identity.email),
            ).fetchone()
            if not req:
                raise ServiceError(409, "Không huỷ được request này")
            self._audit(conn, identity.email, "cancelled", "ok", req)

    def create_link(self, identity: Identity, request_id: int) -> str:
        token = secrets.token_urlsafe(32)
        with self.db.tx() as conn:
            req = conn.execute(
                "SELECT *, (claim_deadline > now()) AS in_window FROM access_request"
                " WHERE id=%s AND requester_email=%s FOR UPDATE",
                (request_id, identity.email),
            ).fetchone()
            if not req:
                raise ServiceError(404, "Không tìm thấy request")
            if req["status"] != "approved":
                raise ServiceError(409, "Request chưa được duyệt hoặc đã dùng")
            if not req["in_window"]:
                raise ServiceError(410, "Đã quá hạn nhận, hãy gửi request mới")
            conn.execute(
                "INSERT INTO download_link (request_id, token_hash, expires_at)"
                " VALUES (%s, %s, now() + %s)",
                (request_id, hash_token(token), timedelta(seconds=self.settings.link_ttl_seconds)),
            )
            self._audit(conn, identity.email, "link_created", "ok", req)
        return f"{self.settings.public_url}/dl#{token}"

    def download(self, identity: Identity, token: str) -> Download:
        if not _LINK_TOKEN_RE.match(token or ""):
            raise ServiceError(400, "Link không hợp lệ")
        token_hash = hash_token(token)

        with self.db.tx() as conn:
            row = conn.execute(
                "SELECT l.id AS link_id, l.used_at, l.expires_at > now() AS link_valid, r.*"
                " FROM download_link l JOIN access_request r ON r.id = l.request_id WHERE l.token_hash=%s",
                (token_hash,),
            ).fetchone()
        if not row:
            raise ServiceError(404, "Link không hợp lệ")
        if row["requester_email"] != identity.email:
            self._audit_tx(identity.email, "download", "denied", row, detail="người mở link không phải người xin")
            raise ServiceError(403, "Link này không phải của bạn")

        with self.db.tx() as conn:
            # Đánh dấu link đã dùng một cách nguyên tử: 2 lần bấm song song chỉ 1 lần qua
            link = conn.execute(
                "UPDATE download_link SET used_at=now() WHERE id=%s AND used_at IS NULL AND expires_at > now()"
                " RETURNING id",
                (row["link_id"],),
            ).fetchone()
            req = None
            if link:
                req = conn.execute(
                    "UPDATE access_request SET status='issuing', issuing_started_at=now(), updated_at=now()"
                    " WHERE id=%s AND status='approved' AND claim_deadline > now() RETURNING *",
                    (row["id"],),
                ).fetchone()
            if not link or not req:
                raise psycopg.Rollback()  # trả link về chưa dùng
        if not link:
            self._audit_tx(identity.email, "download", "denied", row, detail="link đã dùng hoặc hết hạn")
            raise ServiceError(410, "Link đã dùng hoặc đã hết hạn")
        if not req:
            self._audit_tx(identity.email, "download", "denied", row, detail="request không còn ở trạng thái đã duyệt")
            raise ServiceError(409, "Request đã được cấp, đã huỷ hoặc quá hạn nhận")

        cluster = self.clusters[req["cluster"]]
        # Hỏi lại cluster ngay trước khi cấp: namespace có thể vừa bị chuyển sang draining hoặc gỡ label
        if self.catalog.find(req["cluster"], req["namespace"], fresh=True) is None:
            self._rollback_issue(req, row["link_id"], "namespace không còn mở cho xin quyền")
            raise ServiceError(409, "Namespace đã ngừng cấp quyền (admin gỡ label hoặc đang thu hồi). "
                                    "Liên hệ admin.")
        try:
            if not cluster.namespace_exists(req["namespace"]):
                raise ClusterError("namespace không tồn tại")
            issued = cluster.issue(
                request_id=req["id"],
                email=req["requester_email"],
                namespace=req["namespace"],
                role=req["role"],
                expiration_seconds=req["requested_seconds"],
                instance=self.settings.instance_id,
            )
        except Exception as exc:  # noqa: BLE001
            reason = str(exc) if isinstance(exc, ClusterError) else type(exc).__name__
            log.warning("Cấp kubeconfig cho request %s lỗi: %s", req["id"], reason)
            self._rollback_issue(req, row["link_id"], reason)
            raise ServiceError(502, "Tạo quyền trên cluster lỗi. Link vẫn dùng lại được trong thời hạn, hãy thử lại.") from None

        try:
            with self.db.tx() as conn:
                done = conn.execute(
                    "UPDATE access_request SET status='issued', issued_at=now(), sa_name=%s, token_expires_at=%s,"
                    " last_error=NULL, updated_at=now() WHERE id=%s AND status='issuing' RETURNING *",
                    (issued.sa_name, issued.expires_at, req["id"]),
                ).fetchone()
                if not done:
                    raise RuntimeError("trạng thái request đổi trong lúc cấp")
                requested_until = done["issued_at"] + timedelta(seconds=done["requested_seconds"])
                truncated = (requested_until - issued.expires_at).total_seconds() > TRUNCATION_TOLERANCE_SECONDS
                self._audit(conn, identity.email, "downloaded", "ok", done,
                            detail="API server cắt ngắn thời hạn token" if truncated else None)
        except Exception as exc:  # noqa: BLE001
            log.error("Lưu trạng thái request %s lỗi sau khi đã tạo trên cluster: %s", req["id"], type(exc).__name__)
            self._rollback_issue(req, None, f"lưu DB lỗi: {type(exc).__name__}")
            raise ServiceError(500, "Lỗi lưu trạng thái, đã dọn quyền vừa tạo. Hãy tạo link mới.") from None

        content = build_kubeconfig(
            cluster_name=req["cluster"],
            endpoint=cluster.endpoint,
            namespace=req["namespace"],
            user_name=issued.sa_name,
            token=issued.token,
        )
        return Download(
            filename=kubeconfig_filename(req["cluster"], req["namespace"]),
            content=content,
            sa_name=issued.sa_name,
            expires_at=issued.expires_at,
            truncated=truncated,
        )

    def _rollback_issue(self, req: dict, link_id: int | None, reason: str) -> None:
        """Dọn phần đã tạo trên cluster (theo label request-id), trả link về chưa dùng."""
        cleanup_error = None
        try:
            self.clusters[req["cluster"]].delete_for_request(
                request_id=req["id"], namespace=req["namespace"], instance=self.settings.instance_id
            )
        except Exception as exc:  # noqa: BLE001
            cleanup_error = str(exc) if isinstance(exc, ClusterError) else type(exc).__name__
            log.error("Dọn tài nguyên request %s lỗi, job dọn dẹp sẽ quét lại: %s", req["id"], cleanup_error)
        detail = reason + (f"; dọn dẹp lỗi: {cleanup_error}" if cleanup_error else "")
        with self.db.tx() as conn:
            if link_id is not None:
                conn.execute(
                    "UPDATE download_link SET used_at=NULL WHERE id=%s AND expires_at > now()", (link_id,)
                )
            conn.execute(
                "UPDATE access_request SET status='approved', issuing_started_at=NULL, last_error=%s,"
                " updated_at=now() WHERE id=%s AND status IN ('issuing','issued')",
                (detail[:500], req["id"]),
            )
            self._audit(conn, req["requester_email"], "download", "error", req, detail=detail[:500])

    # ------------------------------------------------------------------ admin
    def list_requests(self, status: str | None = None, limit: int = 200) -> list[dict]:
        with self.db.tx() as conn:
            if status:
                return conn.execute(
                    "SELECT * FROM access_request WHERE status=%s ORDER BY id DESC LIMIT %s", (status, limit)
                ).fetchall()
            return conn.execute("SELECT * FROM access_request ORDER BY id DESC LIMIT %s", (limit,)).fetchall()

    def list_issued(self, limit: int = 500) -> list[dict]:
        with self.db.tx() as conn:
            return conn.execute(
                "SELECT * FROM access_request WHERE status IN ('issued','revoke_failed','issuing')"
                " ORDER BY token_expires_at NULLS LAST LIMIT %s",
                (limit,),
            ).fetchall()

    def recent_audit(self, limit: int = 200) -> list[dict]:
        with self.db.tx() as conn:
            return conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT %s", (limit,)).fetchall()

    def approve(self, admin: Identity, request_id: int) -> None:
        with self.db.tx() as conn:
            req = conn.execute("SELECT * FROM access_request WHERE id=%s FOR UPDATE", (request_id,)).fetchone()
            if not req:
                raise ServiceError(404, "Không tìm thấy request")
            if req["status"] != "pending":
                raise ServiceError(409, "Request không ở trạng thái chờ duyệt")
            if req["requester_email"] == admin.email and not self.settings.allow_self_approve:
                denied = req
            elif namespace_forbidden(req["namespace"], self.settings):
                raise ServiceError(403, "Namespace nằm trong danh sách cấm")
            elif self.catalog.find(req["cluster"], req["namespace"], fresh=True) is None:
                # Admin đã gỡ label hoặc chuyển sang draining sau khi dev gửi request
                raise ServiceError(409, "Namespace không còn mở cho xin quyền, hãy từ chối request này")
            else:
                denied = None
                req = conn.execute(
                    "UPDATE access_request SET status='approved', decided_by=%s, decided_at=now(),"
                    " claim_deadline=now() + %s, updated_at=now() WHERE id=%s RETURNING *",
                    (admin.email, timedelta(seconds=self.settings.claim_window_seconds), request_id),
                ).fetchone()
                self._audit(conn, admin.email, "approved", "ok", req)
        if denied:
            self._audit_tx(admin.email, "approved", "denied", denied, detail="admin tự duyệt request của mình")
            raise ServiceError(403, "Không được tự duyệt request của chính mình")

    def reject(self, admin: Identity, request_id: int, reason: str) -> None:
        reason = (reason or "").strip()[:500] or None
        with self.db.tx() as conn:
            req = conn.execute(
                "UPDATE access_request SET status='rejected', decided_by=%s, decided_at=now(), reject_reason=%s,"
                " updated_at=now() WHERE id=%s AND status='pending' RETURNING *",
                (admin.email, reason, request_id),
            ).fetchone()
            if not req:
                raise ServiceError(409, "Request không ở trạng thái chờ duyệt")
            self._audit(conn, admin.email, "rejected", "ok", req, detail=reason)

    def revoke(self, admin: Identity, request_id: int) -> str:
        with self.db.tx() as conn:
            req = conn.execute("SELECT * FROM access_request WHERE id=%s FOR UPDATE", (request_id,)).fetchone()
            if not req:
                raise ServiceError(404, "Không tìm thấy request")
            status = req["status"]
            if status in ("pending", "approved"):
                # Chưa có gì trên cluster: chỉ đổi trạng thái
                req = conn.execute(
                    "UPDATE access_request SET status='revoked', revoked_by=%s, revoked_at=now(), updated_at=now()"
                    " WHERE id=%s RETURNING *",
                    (admin.email, request_id),
                ).fetchone()
                self._audit(conn, admin.email, "revoked", "ok", req, detail="chưa tải, chỉ đổi trạng thái")
                return "revoked"
            if status == "issuing":
                raise ServiceError(409, "Request đang được cấp, thử lại sau ít giây")
            if status not in ("issued", "revoke_failed"):
                raise ServiceError(409, f"Không revoke được request ở trạng thái {status}")
            # Giữ khoá dòng trong lúc xoá để job dọn dẹp không xử lý song song
            try:
                self.clusters[req["cluster"]].delete_for_request(
                    request_id=request_id, namespace=req["namespace"], instance=self.settings.instance_id
                )
                new_status, error, result = "revoked", None, "ok"
            except Exception as exc:  # noqa: BLE001
                error = str(exc) if isinstance(exc, ClusterError) else type(exc).__name__
                new_status, result = "revoke_failed", "error"
            req = conn.execute(
                "UPDATE access_request SET status=%s, revoked_by=%s, revoked_at=now(), last_error=%s,"
                " updated_at=now() WHERE id=%s RETURNING *",
                (new_status, admin.email, error, request_id),
            ).fetchone()
            self._audit(conn, admin.email, "revoked", result, req, detail=error)
            return new_status
