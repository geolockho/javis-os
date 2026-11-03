"""Render các template kubeconfig-generator bằng dữ liệu giả để xem trước giao diện.

Chạy (từ thư mục brain):
  D:\\FSEL\\other-services\\kubeconfig-generator\\.venv\\Scripts\\python.exe workspace\\kubeconfig-generator-preview\\render_preview.py
Kết quả: các file *.html cạnh script này, mở thẳng bằng trình duyệt.
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
APP_ROOT = HERE.parent / "kubeconfig-generator"
sys.path.insert(0, str(APP_ROOT))
os.environ.setdefault("KG_SKIP", "1")

from app.main import TEMPLATES  # noqa: E402

env = TEMPLATES.env
now = datetime.now(timezone.utc)


def req(path):
    return SimpleNamespace(url=SimpleNamespace(path=path))


dev = SimpleNamespace(email="dev.a@fpt.com", is_admin=False)
adm = SimpleNamespace(email="phuhm@fpt.com", is_admin=True)


def row(i, st, ns, cl="fsel-local", **kw):
    base = dict(id=i, cluster=cl, namespace=ns, role="view", status=st, requested_seconds=8 * 3600,
                created_at=now - timedelta(hours=i), requester_email="dev.a@fpt.com", decided_by=None,
                claim_deadline=None, issued_at=None, token_expires_at=None, reject_reason=None,
                last_error=None, sa_name=None)
    base.update(kw)
    return base


rows = [
    row(41, "issued", "ticket", issued_at=now - timedelta(hours=2), token_expires_at=now + timedelta(hours=6),
        decided_by="phuhm@fpt.com", sa_name="kg-41-dev-a"),
    row(40, "issued", "jira", cl="fsel-prod", issued_at=now - timedelta(hours=7, minutes=40),
        token_expires_at=now + timedelta(minutes=20), decided_by="phuhm@fpt.com", sa_name="kg-40-dev-a"),
    row(39, "approved", "payment", claim_deadline=now + timedelta(hours=20), decided_by="phuhm@fpt.com"),
    row(38, "pending", "notification", cl="fsel-prod"),
    row(37, "rejected", "billing", reject_reason="Namespace prod, cần ticket change"),
    row(36, "expired", "ticket", token_expires_at=now - timedelta(days=1)),
    row(35, "revoked", "search", cl="fsel-prod"),
    row(34, "cancelled", "report"),
]
options = {
    "fsel-local": ["ticket", "jira", "payment", "billing", "search", "report", "notification", "auth", "gateway"],
    "fsel-prod": ["ticket", "jira", "notification", "search"],
}
expirations = [(3600, "1 giờ"), (8 * 3600, "8 giờ"), (86400, "1 ngày"), (3 * 86400, "3 ngày"), (7 * 86400, "7 ngày")]
audit = [
    SimpleNamespace(id=900 - i, at=now - timedelta(minutes=7 * i), actor=a, action=act, result=res,
                    request_id=41 - i % 5, requester_email="dev.a@fpt.com", cluster="fsel-local", namespace="ticket",
                    role="view", approver="phuhm@fpt.com", downloaded_at=now if act == "downloaded" else None,
                    token_expires_at=now + timedelta(hours=6), detail=d)
    for i, (a, act, res, d) in enumerate([
        ("dev.a@fpt.com", "downloaded", "ok", None), ("dev.a@fpt.com", "link_created", "ok", None),
        ("phuhm@fpt.com", "approved", "ok", None), ("dev.a@fpt.com", "request_created", "ok", None),
        ("dev.b@fpt.com", "download", "error", "Token đã dùng"), ("phuhm@fpt.com", "rejected", "ok", "cần ticket change"),
    ])
]

pages = {
    "index.html": ("/", {"identity": dev, "options": options, "expirations": expirations, "rows": rows,
                         "msg": "Đã gửi request #41, chờ admin duyệt", "err": ""}),
    "index-empty.html": ("/", {"identity": dev, "options": {}, "expirations": expirations, "rows": [], "msg": "", "err": ""}),
    "admin.html": ("/admin", {"identity": adm, "rows": [dict(r, requester_email=e) for r, e in
                                                         zip(rows, ["dev.a@fpt.com", "dev.b@fpt.com"] * 4)],
                              "issued": [r for r in rows if r["status"] == "issued"], "status": None,
                              "allow_self_approve": False, "msg": "", "err": "Thu hồi #12 lỗi trên cluster, job dọn dẹp sẽ thử lại"}),
    "audit.html": ("/admin/audit", {"identity": adm, "rows": audit}),
    "download.html": ("/dl", {"identity": dev}),
    "error.html": ("/x", {"message": "Bạn không có quyền vào trang này"}),
}

for name, (path, ctx) in pages.items():
    tpl = name.replace("-empty", "")
    html = env.get_template(tpl).render(request=req(path), **ctx)
    (HERE / name).write_text(html, encoding="utf-8")
    print("ok", name, len(html))

# Kiểm nhanh: trang dev không được lộ đường dẫn quản trị (test_flow dòng 96)
assert "/admin" not in (HERE / "index.html").read_text(encoding="utf-8")
assert 'href="/admin"' in (HERE / "admin.html").read_text(encoding="utf-8")
print("checks ok")
