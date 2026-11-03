"""Job dọn dẹp chạy bằng thread trong app (1 replica), có pg advisory lock chống chạy trùng.

Mỗi lượt:
1. Request đã duyệt quá hạn nhận -> expired (chỉ DB).
2. Request đã cấp mà token hết hạn -> xoá SA + RoleBinding theo label -> expired.
3. Request revoke lỗi -> thử xoá lại -> revoked.
4. Request kẹt ở 'issuing' (app chết giữa chừng) -> dọn theo label -> trả về approved/expired.
5. Namespace có label kubeconfig-generator/enabled=draining: thu hồi request đã cấp (xoá SA + RoleBinding),
   request đã duyệt chưa tải -> revoked, request chờ duyệt -> rejected.
6. Quét tài nguyên mồ côi trong các namespace còn label (true, draining): có label của tool (đúng instance)
   nhưng request không còn ở trạng thái issuing/issued -> xoá.
"""
from __future__ import annotations

import logging
import threading
from datetime import timedelta

from .db import LOCK_CLEANUP
from .k8s import ClusterError
from .service import Service

log = logging.getLogger(__name__)


def _err(exc: Exception) -> str:
    return str(exc) if isinstance(exc, ClusterError) else type(exc).__name__


class Cleaner:
    def __init__(self, service: Service):
        self.svc = service
        self.settings = service.settings
        self.db = service.db
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------ một lượt
    def run_once(self) -> dict:
        stats = {"skipped": False, "claim_expired": 0, "token_expired": 0, "revoke_retried": 0,
                 "stuck_reset": 0, "drained": 0, "orphans": 0, "errors": 0}
        with self.db.try_advisory_lock(LOCK_CLEANUP) as got:
            if not got:
                stats["skipped"] = True
                log.info("Bản khác đang chạy dọn dẹp, bỏ qua lượt này")
                return stats
            self._expire_unclaimed(stats)
            self._process_rows("issued", "token_expires_at < now()", "expired", "token_expired", stats)
            self._process_rows("revoke_failed", "TRUE", "revoked", "revoke_retried", stats)
            self._reset_stuck(stats)
            self._drain(stats)
            self._sweep_orphans(stats)
        if any(v for k, v in stats.items() if k != "skipped"):
            log.info("Dọn dẹp xong: %s", stats)
        return stats

    def _expire_unclaimed(self, stats: dict) -> None:
        with self.db.tx() as conn:
            rows = conn.execute(
                "UPDATE access_request SET status='expired', updated_at=now()"
                " WHERE status='approved' AND claim_deadline <= now() RETURNING *"
            ).fetchall()
            for r in rows:
                self.svc._audit(conn, "system", "claim_expired", "ok", r)
        stats["claim_expired"] += len(rows)

    def _ids(self, status: str, where: str) -> list[int]:
        with self.db.tx() as conn:
            return [r["id"] for r in conn.execute(
                f"SELECT id FROM access_request WHERE status=%s AND {where} ORDER BY id", (status,)  # noqa: S608
            ).fetchall()]

    def _process_rows(self, status: str, where: str, new_status: str, stat_key: str, stats: dict) -> None:
        for rid in self._ids(status, where):
            with self.db.tx() as conn:
                req = conn.execute(
                    f"SELECT * FROM access_request WHERE id=%s AND status=%s AND {where} FOR UPDATE SKIP LOCKED",  # noqa: S608
                    (rid, status),
                ).fetchone()
                if not req:
                    continue
                try:
                    self.svc.clusters[req["cluster"]].delete_for_request(
                        request_id=rid, namespace=req["namespace"], instance=self.settings.instance_id
                    )
                except Exception as exc:  # noqa: BLE001
                    stats["errors"] += 1
                    conn.execute(
                        "UPDATE access_request SET last_error=%s, updated_at=now() WHERE id=%s",
                        (f"dọn dẹp lỗi: {_err(exc)}"[:500], rid),
                    )
                    self.svc._audit(conn, "system", f"cleanup_{new_status}", "error", req, detail=_err(exc))
                    continue
                req = conn.execute(
                    "UPDATE access_request SET status=%s, last_error=NULL, updated_at=now() WHERE id=%s RETURNING *",
                    (new_status, rid),
                ).fetchone()
                self.svc._audit(conn, "system", f"cleanup_{new_status}", "ok", req)
                stats[stat_key] += 1

    def _reset_stuck(self, stats: dict) -> None:
        stuck = timedelta(seconds=self.settings.issuing_stuck_seconds)
        with self.db.tx() as conn:
            ids = [r["id"] for r in conn.execute(
                "SELECT id FROM access_request WHERE status='issuing' AND issuing_started_at < now() - %s", (stuck,)
            ).fetchall()]
        for rid in ids:
            with self.db.tx() as conn:
                req = conn.execute(
                    "SELECT * FROM access_request WHERE id=%s AND status='issuing' FOR UPDATE SKIP LOCKED", (rid,)
                ).fetchone()
                if not req:
                    continue
                try:
                    self.svc.clusters[req["cluster"]].delete_for_request(
                        request_id=rid, namespace=req["namespace"], instance=self.settings.instance_id
                    )
                except Exception as exc:  # noqa: BLE001
                    stats["errors"] += 1
                    log.warning("Dọn request kẹt %s lỗi: %s", rid, _err(exc))
                    continue
                req = conn.execute(
                    "UPDATE access_request SET status = CASE WHEN claim_deadline > now() THEN 'approved'"
                    " ELSE 'expired' END, issuing_started_at=NULL, last_error='kẹt ở bước cấp, đã dọn',"
                    " updated_at=now() WHERE id=%s RETURNING *",
                    (rid,),
                ).fetchone()
                self.svc._audit(conn, "system", "cleanup_stuck_issuing", "ok", req)
                stats["stuck_reset"] += 1

    def _drain(self, stats: dict) -> None:
        """Thu hồi mọi quyền ở namespace đang draining. Tool vẫn còn RoleBinding (Kyverno giữ cho draining)."""
        for g in self.svc.catalog.draining():
            with self.db.tx() as conn:
                ids = [r["id"] for r in conn.execute(
                    "SELECT id FROM access_request WHERE cluster=%s AND namespace=%s"
                    " AND status IN ('pending','approved','issued') ORDER BY id",
                    (g.cluster, g.namespace),
                ).fetchall()]
            for rid in ids:
                self._drain_one(rid, g.cluster, g.namespace, stats)

    def _drain_one(self, rid: int, cluster: str, namespace: str, stats: dict) -> None:
        reason = "namespace chuyển sang draining"
        with self.db.tx() as conn:
            req = conn.execute(
                "SELECT * FROM access_request WHERE id=%s AND status IN ('pending','approved','issued')"
                " FOR UPDATE SKIP LOCKED", (rid,)
            ).fetchone()
            if not req:
                return
            if req["status"] == "pending":
                req = conn.execute(
                    "UPDATE access_request SET status='rejected', decided_by='system', decided_at=now(),"
                    " reject_reason=%s, updated_at=now() WHERE id=%s RETURNING *",
                    (reason, rid),
                ).fetchone()
                self.svc._audit(conn, "system", "cleanup_drained", "ok", req, detail=reason)
                stats["drained"] += 1
                return
            if req["status"] == "issued":
                try:
                    self.svc.clusters[cluster].delete_for_request(
                        request_id=rid, namespace=namespace, instance=self.settings.instance_id
                    )
                except Exception as exc:  # noqa: BLE001
                    # Để revoke_failed: lượt sau bước "revoke lỗi" sẽ thử lại
                    stats["errors"] += 1
                    req = conn.execute(
                        "UPDATE access_request SET status='revoke_failed', revoked_by='system', revoked_at=now(),"
                        " last_error=%s, updated_at=now() WHERE id=%s RETURNING *",
                        (f"{reason}; xoá lỗi: {_err(exc)}"[:500], rid),
                    ).fetchone()
                    self.svc._audit(conn, "system", "cleanup_drained", "error", req, detail=_err(exc))
                    return
            req = conn.execute(
                "UPDATE access_request SET status='revoked', revoked_by='system', revoked_at=now(),"
                " last_error=NULL, updated_at=now() WHERE id=%s RETURNING *",
                (rid,),
            ).fetchone()
            self.svc._audit(conn, "system", "cleanup_drained", "ok", req, detail=reason)
            stats["drained"] += 1

    def _sweep_orphans(self, stats: dict) -> None:
        namespaces = self.svc.catalog.namespaces_by_cluster()
        for cluster_name, cluster in self.svc.clusters.items():
            for ns in namespaces.get(cluster_name, []):
                try:
                    ids = cluster.list_owned_request_ids(namespace=ns, instance=self.settings.instance_id)
                except Exception as exc:  # noqa: BLE001
                    stats["errors"] += 1
                    log.warning("Không liệt kê được %s/%s: %s", cluster_name, ns, _err(exc))
                    continue
                for rid in sorted(ids):
                    self._delete_orphan(cluster_name, cluster, ns, rid, stats)

    def _delete_orphan(self, cluster_name: str, cluster, ns: str, rid: int, stats: dict) -> None:
        with self.db.tx() as conn:
            # Khoá dòng request (nếu có) để không đua với bước cấp đang chạy
            req = conn.execute(
                "SELECT * FROM access_request WHERE id=%s FOR UPDATE", (rid,)
            ).fetchone()
            if req and req["status"] in ("issuing", "issued") and req["cluster"] == cluster_name \
                    and req["namespace"] == ns:
                return
            try:
                cluster.delete_for_request(request_id=rid, namespace=ns, instance=self.settings.instance_id)
            except Exception as exc:  # noqa: BLE001
                stats["errors"] += 1
                log.warning("Xoá tài nguyên mồ côi %s/%s request %s lỗi: %s", cluster_name, ns, rid, _err(exc))
                return
            self.svc._audit(conn, "system", "cleanup_orphan", "ok", req, request_id=rid, cluster=cluster_name,
                            namespace=ns)
            stats["orphans"] += 1

    # ------------------------------------------------------------ thread
    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="cleanup", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)

    def _loop(self) -> None:
        # Chạy ngay một lượt khi khởi động để bù lúc app tắt
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:  # noqa: BLE001
                log.exception("Lượt dọn dẹp lỗi")
            self._stop.wait(self.settings.cleanup_interval_seconds)
