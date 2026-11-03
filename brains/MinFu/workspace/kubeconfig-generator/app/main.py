"""Web app FastAPI. Chạy sau oauth2-proxy (sidecar), chỉ nghe 127.0.0.1."""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from . import ratelimit
from .auth import Identity, client_ip, identity_from_request, require_admin
from .config import Settings, format_duration, load_settings
from .k8s import LABEL_NS_ENABLED, NS_STATE_DRAINING, NS_STATE_ENABLED
from .logging_redact import redact, setup_logging
from .service import Service, ServiceError

log = logging.getLogger("kubeconfig_generator")
access_log = logging.getLogger("kubeconfig_generator.access")

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

STATUS_LABELS = {
    "pending": "Chờ duyệt",
    "approved": "Đã duyệt, chờ tải",
    "rejected": "Bị từ chối",
    "cancelled": "Đã huỷ",
    "issuing": "Đang cấp",
    "issued": "Đã cấp",
    "expired": "Hết hạn",
    "revoked": "Đã thu hồi",
    "revoke_failed": "Thu hồi lỗi",
}
TEMPLATES.env.globals["STATUS_LABELS"] = STATUS_LABELS
TEMPLATES.env.filters["duration"] = format_duration
TEMPLATES.env.filters["dt"] = lambda v: v.astimezone().strftime("%Y-%m-%d %H:%M") if v else ""

# Header danh tính không bao giờ được in ra (kể cả ở trang debug)
SENSITIVE_HEADERS = {"authorization", "cookie", "x-forwarded-access-token", "x-auth-request-access-token",
                     "x-forwarded-id-token", "x-auth-request-id-token"}


def _build_service(settings: Settings) -> Service:
    from .catalog import NamespaceCatalog
    from .db import Database
    from .k8s import KubeCluster

    db = Database(settings.database_url)
    db.migrate()
    clusters = {name: KubeCluster(name, c.kubeconfig_path) for name, c in settings.clusters.items()}
    return Service(settings, db, clusters, NamespaceCatalog(clusters, settings))


def create_app(settings: Settings | None = None, service: Service | None = None,
               start_cleaner: bool = True) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal service
        if service is None:
            service = _build_service(settings)
        app.state.service = service
        cleaner = None
        if start_cleaner:
            from .cleanup import Cleaner

            cleaner = Cleaner(service)
            cleaner.start()
        yield
        if cleaner:
            cleaner.stop()

    app = FastAPI(title="kubeconfig-generator", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    if service is not None:
        app.state.service = service

    global_limiter = ratelimit.per_second(settings.rate_limit_per_second)
    link_limiter = ratelimit.per_minute(settings.link_rate_per_minute)
    download_limiter = ratelimit.per_minute(settings.download_rate_per_minute)

    # ------------------------------------------------------------ middleware
    @app.middleware("http")
    async def guard(request: Request, call_next):
        start = time.monotonic()
        ip = client_ip(request, settings)
        path = request.url.path
        if path not in ("/healthz", "/readyz") and not global_limiter.allow(ip):
            return JSONResponse({"detail": "Quá nhiều request, chậm lại"}, status_code=429)
        if request.method == "POST" and not _same_origin(request, settings):
            return JSONResponse({"detail": "Sai nguồn gửi (CSRF)"}, status_code=403)
        response = await call_next(request)
        # Không dùng no-referrer: Chrome sẽ gửi "Origin: null" cho form POST cùng origin và _same_origin chặn nhầm
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Cache-Control", "no-store")
        if path not in ("/healthz", "/readyz"):
            # Không ghi query string; đường dẫn đã lọc
            access_log.info("%s %s %s %s %.0fms", ip, request.method, redact(path), response.status_code,
                            (time.monotonic() - start) * 1000)
        return response

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        if _wants_json(request):
            return JSONResponse({"detail": exc.message}, status_code=exc.status)
        return _render(request, "error.html", {"message": exc.message}, status=exc.status)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        if _wants_json(request):
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        return _render(request, "error.html", {"message": exc.detail}, status=exc.status_code)

    # ------------------------------------------------------------ deps
    def svc(request: Request) -> Service:
        return request.app.state.service

    def user(request: Request) -> Identity:
        return identity_from_request(request, settings)

    def admin(identity: Identity = Depends(user)) -> Identity:
        return require_admin(identity)

    # ------------------------------------------------------------ health
    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz(request: Request):
        ok = request.app.state.service.db.ping()
        return JSONResponse({"status": "ok" if ok else "db_error"}, status_code=200 if ok else 503)

    # ------------------------------------------------------------ dev
    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, identity: Identity = Depends(user), service: Service = Depends(svc)):
        options = service.form_options(identity)
        rows = service.my_requests(identity.email)
        return _render(request, "index.html", {
            "identity": identity,
            "options": options,
            "expirations": [(s, format_duration(s)) for s in settings.expiration_options],
            "rows": rows,
            "msg": request.query_params.get("msg", ""),
            "err": request.query_params.get("err", ""),
        })

    @app.post("/requests")
    async def create_request(request: Request, cluster: str = Form(...), namespace: str = Form(...),
                             expiration: int = Form(...), identity: Identity = Depends(user),
                             service: Service = Depends(svc)):
        try:
            rid = await run_in_threadpool(service.create_request, identity, cluster, namespace, expiration)
        except ServiceError as exc:
            return _redirect("/", err=exc.message)
        return _redirect("/", msg=f"Đã gửi request #{rid}, chờ admin duyệt")

    @app.post("/requests/{request_id}/cancel")
    async def cancel(request_id: int, identity: Identity = Depends(user), service: Service = Depends(svc)):
        try:
            await run_in_threadpool(service.cancel_request, identity, request_id)
        except ServiceError as exc:
            return _redirect("/", err=exc.message)
        return _redirect("/", msg=f"Đã huỷ request #{request_id}")

    @app.get("/api/my-requests")
    def my_requests_api(identity: Identity = Depends(user), service: Service = Depends(svc)):
        return [_public_row(r) for r in service.my_requests(identity.email)]

    @app.post("/api/requests/{request_id}/link")
    async def create_link(request_id: int, identity: Identity = Depends(user), service: Service = Depends(svc)):
        if not link_limiter.allow(identity.email):
            raise HTTPException(429, "Tạo link quá nhiều, chờ một chút")
        url = await run_in_threadpool(service.create_link, identity, request_id)
        return {"url": url, "ttl": format_duration(settings.link_ttl_seconds)}

    @app.get("/dl", response_class=HTMLResponse)
    def download_page(request: Request, identity: Identity = Depends(user)):
        # Token nằm sau dấu '#', trình duyệt không gửi lên server và không lọt vào access log
        return _render(request, "download.html", {"identity": identity})

    @app.post("/dl")
    async def download(request: Request, token: str = Form(...), identity: Identity = Depends(user),
                       service: Service = Depends(svc)):
        ip = client_ip(request, settings)
        if not download_limiter.allow(ip):
            raise HTTPException(429, "Thử tải quá nhiều, chờ một chút")
        result = await run_in_threadpool(service.download, identity, token)
        headers = {
            "Content-Disposition": f'attachment; filename="{result.filename}"',
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "X-Token-Expires-At": result.expires_at.isoformat(),
        }
        if result.truncated:
            headers["X-Token-Truncated"] = "true"
        return Response(content=result.content, media_type="application/yaml", headers=headers)

    # ------------------------------------------------------------ admin
    @app.get("/admin", response_class=HTMLResponse)
    def admin_page(request: Request, identity: Identity = Depends(admin), service: Service = Depends(svc)):
        status = request.query_params.get("status") or None
        if status and status not in STATUS_LABELS:
            status = None
        return _render(request, "admin.html", {
            "identity": identity,
            "rows": service.list_requests(status),
            "issued": service.list_issued(),
            "status": status,
            "allow_self_approve": settings.allow_self_approve,
            "msg": request.query_params.get("msg", ""),
            "err": request.query_params.get("err", ""),
        })

    @app.post("/admin/requests/{request_id}/approve")
    async def approve(request_id: int, identity: Identity = Depends(admin), service: Service = Depends(svc)):
        try:
            await run_in_threadpool(service.approve, identity, request_id)
        except ServiceError as exc:
            return _redirect("/admin", err=exc.message)
        return _redirect("/admin", msg=f"Đã duyệt #{request_id}")

    @app.post("/admin/requests/{request_id}/reject")
    async def reject(request_id: int, reason: str = Form(""), identity: Identity = Depends(admin),
                     service: Service = Depends(svc)):
        try:
            await run_in_threadpool(service.reject, identity, request_id, reason)
        except ServiceError as exc:
            return _redirect("/admin", err=exc.message)
        return _redirect("/admin", msg=f"Đã từ chối #{request_id}")

    @app.post("/admin/requests/{request_id}/revoke")
    async def revoke(request_id: int, identity: Identity = Depends(admin), service: Service = Depends(svc)):
        try:
            status = await run_in_threadpool(service.revoke, identity, request_id)
        except ServiceError as exc:
            return _redirect("/admin", err=exc.message)
        if status == "revoke_failed":
            return _redirect("/admin", err=f"Thu hồi #{request_id} lỗi trên cluster, job dọn dẹp sẽ thử lại")
        return _redirect("/admin", msg=f"Đã thu hồi #{request_id}")

    @app.get("/admin/audit", response_class=HTMLResponse)
    def audit_page(request: Request, identity: Identity = Depends(admin), service: Service = Depends(svc)):
        return _render(request, "audit.html", {"identity": identity, "rows": service.recent_audit()})

    @app.get("/admin/debug/claims")
    def debug_claims(request: Request, identity: Identity = Depends(admin), service: Service = Depends(svc)):
        """In ra những gì oauth2-proxy truyền vào (email, IP) và namespace đang mở theo label.

        Không in token/cookie."""
        headers = {}
        for k, v in request.headers.items():
            lk = k.lower()
            if lk in SENSITIVE_HEADERS:
                continue
            if lk.startswith(("x-forwarded-", "x-auth-request-", "x-real-ip", "gap-")):
                headers[k] = redact(v)
        return {
            "email": identity.email,
            "is_admin": identity.is_admin,
            "email_header": settings.email_header,
            "client_ip": client_ip(request, settings),
            "client_ip_header": settings.client_ip_header,
            "namespace_label": f"{LABEL_NS_ENABLED}={NS_STATE_ENABLED}|{NS_STATE_DRAINING}",
            "catalog": [_grant_dict(g) for g in service.catalog.grants()],
            "draining": [_grant_dict(g) for g in service.catalog.draining()],
            "catalog_errors": dict(service.catalog.last_error),
            "headers": headers,
        }

    return app


# ------------------------------------------------------------ helpers
def _same_origin(request: Request, settings: Settings) -> bool:
    origin = request.headers.get("origin")
    if origin and origin.lower() != "null":
        return origin.rstrip("/").lower() == settings.public_origin
    site = request.headers.get("sec-fetch-site")
    if site:
        return site in ("same-origin", "none")
    return True


def _wants_json(request: Request) -> bool:
    return request.url.path.startswith(("/api/", "/admin/debug")) or \
        "application/json" in request.headers.get("accept", "")


def _redirect(path: str, msg: str = "", err: str = "") -> RedirectResponse:
    q = f"?msg={quote(msg)}" if msg else (f"?err={quote(err)}" if err else "")
    return RedirectResponse(path + q, status_code=303)


def _render(request: Request, name: str, ctx: dict, status: int = 200) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(request, name, ctx, status_code=status)


def _grant_dict(g) -> dict:
    return {"cluster": g.cluster, "namespace": g.namespace, "role": g.role, "state": g.state}


def _public_row(r: dict) -> dict:
    keys = ("id", "cluster", "namespace", "role", "status", "requested_seconds", "created_at", "decided_by",
            "claim_deadline", "issued_at", "token_expires_at", "reject_reason")
    out = {k: r.get(k) for k in keys}
    for k, v in out.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
    out["status_label"] = STATUS_LABELS.get(r["status"], r["status"])
    return out


def run() -> None:
    import uvicorn

    settings = load_settings()
    setup_logging(settings.log_level)
    uvicorn.run(create_app(settings), host="127.0.0.1", port=8000, workers=1, access_log=False,
                proxy_headers=False, log_config=None)


if __name__ == "__main__":
    run()
