"""Nghiệm thu mục 7 với PostgreSQL thật và cluster giả (FakeCluster).

Chạy: TEST_DATABASE_URL=postgresql://postgres:test@localhost:55432/postgres pytest
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import psycopg
import pytest
import yaml

from app.auth import Identity
from app.cleanup import Cleaner
from app.db import LOCK_CLEANUP
from app.k8s import labels_for
from app.service import ServiceError

from .conftest import ADMIN, ADMIN2, DEV, DEV_B, FAKE_JWT, hdr

pytestmark = pytest.mark.db

DAY = 86400


# ------------------------------------------------------------------ helpers
def flash(resp) -> dict:
    assert resp.status_code == 303, resp.text
    q = parse_qs(urlparse(resp.headers["location"]).query)
    return {k: v[0] for k, v in q.items()}


def submit(client, email=DEV, cluster="fsel-local", ns="team-a", exp=DAY):
    resp = client.post("/requests", data={"cluster": cluster, "namespace": ns, "expiration": exp},
                       headers=hdr(email), follow_redirects=False)
    return flash(resp)


def last_request(service, email=DEV) -> dict:
    return service.my_requests(email)[0]


def approve(client, rid, admin=ADMIN):
    return flash(client.post(f"/admin/requests/{rid}/approve", headers=hdr(admin), follow_redirects=False))


def make_link(client, rid, email=DEV) -> str:
    resp = client.post(f"/api/requests/{rid}/link", headers=hdr(email))
    assert resp.status_code == 200, resp.text
    url = resp.json()["url"]
    assert url.startswith("https://kubeconfig-generator.fsel.edu.vn/dl#")
    return url.split("#", 1)[1]


def download(client, token, email=DEV):
    return client.post("/dl", data={"token": token}, headers=hdr(email))


def approved_request(client, service, **kw) -> int:
    assert "msg" in submit(client, **kw)
    rid = last_request(service, kw.get("email", DEV))["id"]
    assert "msg" in approve(client, rid)
    return rid


def status_of(service, rid) -> str:
    with service.db.tx() as conn:
        return conn.execute("SELECT status FROM access_request WHERE id=%s", (rid,)).fetchone()["status"]


def all_objects(clusters) -> list[dict]:
    return [o for c in clusters.values() for o in c.objects]


# ------------------------------------------------------------------ xác thực / admin
def test_unauthenticated_is_401(client):
    assert client.get("/").status_code == 401
    assert client.post("/requests", data={"cluster": "fsel-local", "namespace": "team-a", "expiration": DAY}
                       ).status_code == 401


@pytest.mark.parametrize("method,path", [
    ("get", "/admin"), ("get", "/admin/audit"), ("get", "/admin/debug/claims"),
    ("post", "/admin/requests/1/approve"), ("post", "/admin/requests/1/reject"),
    ("post", "/admin/requests/1/revoke"),
])
def test_non_admin_gets_403_on_admin_endpoints(client, method, path):
    resp = getattr(client, method)(path, headers=hdr(DEV), follow_redirects=False)
    assert resp.status_code == 403


def test_admin_link_hidden_for_dev(client):
    assert "/admin" not in client.get("/", headers=hdr(DEV)).text
    assert 'href="/admin"' in client.get("/", headers=hdr(ADMIN)).text


def test_csrf_foreign_origin_blocked(client):
    resp = client.post("/requests", data={"cluster": "fsel-local", "namespace": "team-a", "expiration": DAY},
                       headers={**hdr(DEV), "Origin": "https://evil.example"})
    assert resp.status_code == 403


def test_csrf_null_origin_follows_fetch_site(client):
    form = {"cluster": "fsel-local", "namespace": "team-a", "expiration": DAY}
    blocked = client.post("/requests", data=form, follow_redirects=False,
                          headers={**hdr(DEV), "Origin": "null", "Sec-Fetch-Site": "cross-site"})
    assert blocked.status_code == 403
    ok = client.post("/requests", data=form, follow_redirects=False,
                     headers={**hdr(DEV), "Origin": "null", "Sec-Fetch-Site": "same-origin"})
    assert ok.status_code != 403


def test_referrer_policy_allows_same_origin_origin_header(client):
    resp = client.get("/", headers=hdr(DEV))
    assert resp.headers["referrer-policy"] == "same-origin"


def test_debug_claims_hides_secrets(client):
    resp = client.get("/admin/debug/claims", headers={
        **hdr(ADMIN),
        "X-Forwarded-Access-Token": "secret-access-token",
        "Cookie": "_oauth2_proxy=secret-cookie",
        "X-Forwarded-Preferred-Username": "hophu",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "groups" not in data
    assert {(g["cluster"], g["namespace"]) for g in data["catalog"]} == {
        ("fsel-local", "team-a"), ("fsel-local", "team-b"), ("fsel-prod", "team-a")}
    assert data["draining"] == [] and data["catalog_errors"] == {}
    assert data["is_admin"] is True
    assert "secret-access-token" not in resp.text
    assert "secret-cookie" not in resp.text
    assert data["headers"].get("x-forwarded-preferred-username") == "hophu"


# ------------------------------------------------------------------ danh mục / blacklist
@pytest.mark.parametrize("cluster,ns,exp", [
    ("fsel-local", "team-c", DAY),        # có trên cluster nhưng ngoài danh mục
    ("fsel-prod", "team-b", DAY),         # có trong danh mục của cluster khác
    ("fsel-local", "redis", DAY),         # blacklist
    ("fsel-local", "kube-public", DAY),   # chứa 'kube'
    ("fsel-local", "kube-system", DAY),
    ("fsel-local", "cd", DAY),
    ("other", "team-a", DAY),             # cluster lạ
    ("fsel-local", "team-a", 999_999),    # thời hạn không có trong lựa chọn
    ("fsel-local", "team-a", 200 * DAY),  # vượt 90 ngày
])
def test_tampered_form_rejected_and_nothing_created(client, service, clusters, cluster, ns, exp):
    result = submit(client, cluster=cluster, ns=ns, exp=exp)
    assert "err" in result
    assert service.my_requests(DEV) == []
    assert all_objects(clusters) == []


def test_any_logged_in_user_sees_full_catalog_without_group(client):
    # Không có header group nào: vẫn thấy mọi namespace trong danh mục, không thấy namespace ngoài danh mục
    html = client.get("/", headers=hdr(DEV_B)).text
    for ns in ("team-a", "team-b"):
        assert ns in html
    for ns in ("team-c", "redis", "kube-public"):
        assert ns not in html


def test_any_logged_in_user_can_request_without_group(client, service):
    assert "msg" in submit(client, email=DEV, ns="team-a")
    assert "msg" in submit(client, email=DEV_B, ns="team-b")
    assert [r["namespace"] for r in service.my_requests(DEV_B)] == ["team-b"]


def test_group_header_is_ignored(client, service):
    # Header group (kể cả giả mạo) không mở thêm namespace ngoài danh mục
    resp = client.post("/requests", data={"cluster": "fsel-local", "namespace": "team-c", "expiration": DAY},
                       headers={**hdr(DEV), "X-Forwarded-Groups": "admins,other-services/team-c"},
                       follow_redirects=False)
    assert "err" in flash(resp)
    assert service.my_requests(DEV) == []


@pytest.mark.parametrize("new_state", [None, "draining"])
def test_approve_rejected_when_label_changed(client, service, clusters, new_state):
    assert "msg" in submit(client, ns="team-b")
    rid = last_request(service)["id"]
    clusters["fsel-local"].set_label("team-b", new_state)   # gỡ label hoặc chuyển draining
    assert "err" in approve(client, rid)                     # duyệt luôn hỏi lại cluster, không dùng cache
    assert status_of(service, rid) == "pending"


def test_new_label_opens_namespace(client, service, clusters):
    assert "err" in submit(client, ns="team-c")
    clusters["fsel-local"].set_label("team-c", "true")
    service.catalog.refresh(force=True)
    assert "team-c" in client.get("/", headers=hdr(DEV)).text
    assert "msg" in submit(client, ns="team-c")


def test_draining_namespace_hidden_and_not_requestable(client, service, clusters):
    clusters["fsel-local"].set_label("team-b", "draining")
    service.catalog.refresh(force=True)
    assert "team-b" not in client.get("/", headers=hdr(DEV)).text
    assert "err" in submit(client, ns="team-b")
    assert service.my_requests(DEV) == []


def test_download_blocked_when_drained_after_approve(client, service, clusters):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    clusters["fsel-local"].set_label("team-a", "draining")
    resp = download(client, token)
    assert resp.status_code == 409
    assert all_objects(clusters) == []
    assert clusters["fsel-local"].issue_calls == 0
    assert status_of(service, rid) == "approved"


def test_denied_request_is_audited(client, service):
    submit(client, ns="redis")
    rows = service.recent_audit()
    assert rows[0]["action"] == "request_created" and rows[0]["result"] == "denied"
    assert rows[0]["requester_email"] == DEV


# ------------------------------------------------------------------ chống spam
def test_duplicate_request_blocked(client, service):
    assert "msg" in submit(client)
    assert "err" in submit(client)
    assert len(service.my_requests(DEV)) == 1


def test_pending_limit(client, service):
    service.settings.max_pending_per_user = 1
    assert "msg" in submit(client, cluster="fsel-local")
    assert "err" in submit(client, cluster="fsel-prod")


def test_duplicate_blocked_while_issued(client, service):
    rid = approved_request(client, service)
    assert download(client, make_link(client, rid)).status_code == 200
    assert "err" in submit(client)


# ------------------------------------------------------------------ duyệt
def test_rejected_request_creates_nothing(client, service, clusters):
    submit(client)
    rid = last_request(service)["id"]
    r = flash(client.post(f"/admin/requests/{rid}/reject", data={"reason": "không cần"}, headers=hdr(ADMIN),
                          follow_redirects=False))
    assert "msg" in r
    assert status_of(service, rid) == "rejected"
    assert last_request(service)["reject_reason"] == "không cần"
    assert client.post(f"/api/requests/{rid}/link", headers=hdr(DEV)).status_code == 409
    assert all_objects(clusters) == []


def test_approved_but_not_downloaded_creates_nothing(client, service, clusters):
    rid = approved_request(client, service)
    assert status_of(service, rid) == "approved"
    make_link(client, rid)
    assert all_objects(clusters) == []
    assert all(c.issue_calls == 0 for c in clusters.values())


def test_admin_cannot_self_approve(client, service):
    assert "msg" in submit(client, email=ADMIN)
    rid = last_request(service, ADMIN)["id"]
    assert "err" in approve(client, rid, admin=ADMIN)
    assert status_of(service, rid) == "pending"
    assert "msg" in approve(client, rid, admin=ADMIN2)   # admin khác thì duyệt được


def test_self_approve_allowed_when_flag_on(client, service):
    service.settings.allow_self_approve = True
    submit(client, email=ADMIN)
    rid = last_request(service, ADMIN)["id"]
    assert "msg" in approve(client, rid, admin=ADMIN)


# ------------------------------------------------------------------ tải
def test_full_flow_issues_view_binding_and_kubeconfig(client, service, clusters):
    rid = approved_request(client, service)
    resp = download(client, make_link(client, rid))
    assert resp.status_code == 200
    assert resp.headers["cache-control"] == "no-store"
    assert "attachment" in resp.headers["content-disposition"]
    doc = yaml.safe_load(resp.text)
    assert doc["contexts"][0]["context"]["namespace"] == "team-a"
    assert doc["clusters"][0]["cluster"]["server"] == clusters["fsel-local"].endpoint.server
    assert doc["clusters"][0]["cluster"]["certificate-authority-data"] == clusters["fsel-local"].endpoint.ca_data

    objs = clusters["fsel-local"].owned(rid)
    assert sorted(o["kind"] for o in objs) == ["RoleBinding", "ServiceAccount"]
    assert [o["role"] for o in objs if o["kind"] == "RoleBinding"] == ["view"]
    assert all(o["namespace"] == "team-a" for o in objs)
    assert clusters["fsel-prod"].objects == []

    req = last_request(service)
    assert req["status"] == "issued"
    assert req["token_expires_at"] is not None
    assert req["sa_name"] == objs[0]["name"]


def test_link_second_use_rejected(client, service, clusters):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    assert download(client, token).status_code == 200
    assert download(client, token).status_code == 410
    assert len(clusters["fsel-local"].owned(rid)) == 2


def test_link_expired_rejected(client, service, clusters):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    with service.db.tx() as conn:
        conn.execute("UPDATE download_link SET expires_at = now() - interval '1 second'")
    assert download(client, token).status_code == 410
    assert all_objects(clusters) == []


def test_link_opened_by_other_user_rejected(client, service, clusters):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    assert download(client, token, email=DEV_B).status_code == 403
    assert all_objects(clusters) == []
    # Người xin vẫn dùng được link
    assert download(client, token).status_code == 200


def test_invalid_token_format(client):
    assert download(client, "short").status_code == 400
    assert download(client, "A" * 43).status_code == 404


def test_claim_window_expired(client, service):
    rid = approved_request(client, service)
    with service.db.tx() as conn:
        conn.execute("UPDATE access_request SET claim_deadline = now() - interval '1 second'")
    assert client.post(f"/api/requests/{rid}/link", headers=hdr(DEV)).status_code == 410


def _parallel(fn, args_list):
    results, barrier = [None] * len(args_list), threading.Barrier(len(args_list))

    def run(i, args):
        barrier.wait()
        try:
            results[i] = fn(*args)
        except ServiceError as exc:
            results[i] = exc

    threads = [threading.Thread(target=run, args=(i, a)) for i, a in enumerate(args_list)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_parallel_clicks_same_link_create_one_sa(client, service, clusters):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    clusters["fsel-local"].issue_delay = 0.3
    ident = Identity(DEV)
    results = _parallel(service.download, [(ident, token)] * 5)
    ok = [r for r in results if not isinstance(r, ServiceError)]
    assert len(ok) == 1
    sas = [o for o in clusters["fsel-local"].owned(rid) if o["kind"] == "ServiceAccount"]
    assert len(sas) == 1


def test_parallel_different_links_create_one_sa(client, service, clusters):
    rid = approved_request(client, service)
    tokens = [make_link(client, rid) for _ in range(3)]
    clusters["fsel-local"].issue_delay = 0.3
    ident = Identity(DEV)
    results = _parallel(service.download, [(ident, t) for t in tokens])
    assert sum(1 for r in results if not isinstance(r, ServiceError)) == 1
    assert len([o for o in clusters["fsel-local"].owned(rid) if o["kind"] == "ServiceAccount"]) == 1


@pytest.mark.parametrize("fail_at", ["rolebinding", "token"])
def test_cluster_failure_leaves_no_orphans_and_link_reusable(client, service, clusters, fail_at):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    clusters["fsel-local"].fail_at = fail_at
    assert download(client, token).status_code == 502
    assert clusters["fsel-local"].owned(rid) == []
    assert status_of(service, rid) == "approved"
    audit = service.recent_audit()
    assert any(a["action"] == "download" and a["result"] == "error" for a in audit)
    # Hết lỗi thì dùng lại đúng link đó được
    clusters["fsel-local"].fail_at = None
    assert download(client, token).status_code == 200
    assert len(clusters["fsel-local"].owned(rid)) == 2


def test_truncated_token_expiry_shown_and_stored(client, service, clusters):
    clusters["fsel-local"].truncate_to = 3600
    rid = approved_request(client, service, exp=30 * DAY)
    resp = download(client, make_link(client, rid))
    assert resp.headers.get("x-token-truncated") == "true"
    req = last_request(service)
    left = (req["token_expires_at"] - datetime.now(timezone.utc)).total_seconds()
    assert 3500 < left <= 3600
    assert any(a["action"] == "downloaded" and "cắt ngắn" in (a["detail"] or "") for a in service.recent_audit())


# ------------------------------------------------------------------ log
def test_tokens_never_logged(client, service, caplog):
    caplog.set_level(logging.DEBUG)
    rid = approved_request(client, service)
    token = make_link(client, rid)
    assert download(client, token).status_code == 200
    download(client, token)                         # lần 2: lỗi 410, cũng không in token
    assert FAKE_JWT not in caplog.text
    assert token not in caplog.text


# ------------------------------------------------------------------ revoke
def test_revoke_deletes_sa_and_binding(client, service, clusters):
    rid = approved_request(client, service)
    download(client, make_link(client, rid))
    assert len(clusters["fsel-local"].owned(rid)) == 2
    assert "msg" in flash(client.post(f"/admin/requests/{rid}/revoke", headers=hdr(ADMIN), follow_redirects=False))
    assert clusters["fsel-local"].owned(rid) == []
    assert status_of(service, rid) == "revoked"


def test_revoke_only_touches_own_request(client, service, clusters):
    rid1 = approved_request(client, service)
    download(client, make_link(client, rid1))
    rid2 = approved_request(client, service, email=DEV_B)
    download(client, make_link(client, rid2, email=DEV_B), email=DEV_B)
    flash(client.post(f"/admin/requests/{rid1}/revoke", headers=hdr(ADMIN), follow_redirects=False))
    assert clusters["fsel-local"].owned(rid1) == []
    assert len(clusters["fsel-local"].owned(rid2)) == 2


def test_revoke_before_download_is_db_only(client, service, clusters):
    rid = approved_request(client, service)
    token = make_link(client, rid)
    flash(client.post(f"/admin/requests/{rid}/revoke", headers=hdr(ADMIN), follow_redirects=False))
    assert status_of(service, rid) == "revoked"
    assert download(client, token).status_code == 409
    assert all_objects(clusters) == []


def test_revoke_failure_kept_and_retried_by_cleanup(client, service, clusters):
    rid = approved_request(client, service)
    download(client, make_link(client, rid))
    clusters["fsel-local"].fail_at = "delete"
    assert "err" in flash(client.post(f"/admin/requests/{rid}/revoke", headers=hdr(ADMIN), follow_redirects=False))
    assert status_of(service, rid) == "revoke_failed"
    clusters["fsel-local"].fail_at = None
    Cleaner(service).run_once()
    assert status_of(service, rid) == "revoked"
    assert clusters["fsel-local"].owned(rid) == []


# ------------------------------------------------------------------ dọn dẹp
def test_cleanup_expires_tokens_and_unclaimed(client, service, clusters):
    rid_issued = approved_request(client, service)
    download(client, make_link(client, rid_issued))
    rid_unclaimed = approved_request(client, service, cluster="fsel-prod")
    with service.db.tx() as conn:
        conn.execute("UPDATE access_request SET token_expires_at = now() - interval '1 second' WHERE id=%s",
                     (rid_issued,))
        conn.execute("UPDATE access_request SET claim_deadline = now() - interval '1 second' WHERE id=%s",
                     (rid_unclaimed,))
    stats = Cleaner(service).run_once()
    assert stats["token_expired"] == 1 and stats["claim_expired"] == 1
    assert status_of(service, rid_issued) == "expired"
    assert status_of(service, rid_unclaimed) == "expired"
    assert clusters["fsel-local"].owned(rid_issued) == []


def test_cleanup_only_deletes_tool_labelled_resources(client, service, clusters):
    local = clusters["fsel-local"]
    # Tài nguyên không phải của tool hoặc của instance khác: phải còn nguyên
    local.objects.append({"kind": "ServiceAccount", "namespace": "team-a", "name": "decoy", "labels": {}})
    local.objects.append({"kind": "ServiceAccount", "namespace": "team-a", "name": "decoy-req",
                          "labels": {"kubeconfig-generator/request-id": "999"}})
    local.objects.append({"kind": "ServiceAccount", "namespace": "team-a", "name": "other-instance",
                          "labels": labels_for(999, DEV, "staging")})
    # Mồ côi của tool (request không tồn tại trong DB): phải bị xoá
    local.objects.append({"kind": "ServiceAccount", "namespace": "team-a", "name": "orphan",
                          "labels": labels_for(999, DEV, "default")})
    # Kubeconfig đang hiệu lực: phải còn
    rid = approved_request(client, service)
    download(client, make_link(client, rid))

    stats = Cleaner(service).run_once()
    names = {o["name"] for o in local.objects}
    assert {"decoy", "decoy-req", "other-instance"} <= names
    assert "orphan" not in names
    assert len(local.owned(rid)) == 2
    assert stats["orphans"] == 1


def test_cleanup_resets_stuck_issuing(client, service, clusters):
    rid = approved_request(client, service)
    local = clusters["fsel-local"]
    local.objects.append({"kind": "ServiceAccount", "namespace": "team-a", "name": "half",
                          "labels": labels_for(rid, DEV, "default")})
    with service.db.tx() as conn:
        conn.execute("UPDATE access_request SET status='issuing', issuing_started_at = now() - interval '1 hour'"
                     " WHERE id=%s", (rid,))
    Cleaner(service).run_once()
    assert status_of(service, rid) == "approved"
    assert local.owned(rid) == []


def test_cleanup_drains_namespace(client, service, clusters):
    local = clusters["fsel-local"]
    rid_issued = approved_request(client, service, ns="team-a")
    download(client, make_link(client, rid_issued))
    rid_approved = approved_request(client, service, email=DEV_B, ns="team-a")
    assert "msg" in submit(client, email=ADMIN2, ns="team-a")
    rid_pending = last_request(service, ADMIN2)["id"]
    rid_other = approved_request(client, service, ns="team-b")          # namespace khác: không đụng
    download(client, make_link(client, rid_other))

    local.set_label("team-a", "draining")
    service.catalog.refresh(force=True)
    stats = Cleaner(service).run_once()

    assert stats["drained"] == 3
    assert status_of(service, rid_issued) == "revoked"
    assert local.owned(rid_issued) == []
    assert status_of(service, rid_approved) == "revoked"
    assert status_of(service, rid_pending) == "rejected"
    assert last_request(service, ADMIN2)["reject_reason"] == "namespace chuyển sang draining"
    assert status_of(service, rid_other) == "issued"
    assert len(local.owned(rid_other)) == 2
    assert any(a["action"] == "cleanup_drained" and a["request_id"] == rid_issued for a in service.recent_audit())
    # Lượt sau không còn gì để thu hồi
    assert Cleaner(service).run_once()["drained"] == 0


def test_drain_delete_failure_retried(client, service, clusters):
    local = clusters["fsel-local"]
    rid = approved_request(client, service)
    download(client, make_link(client, rid))
    local.set_label("team-a", "draining")
    service.catalog.refresh(force=True)
    local.fail_at = "delete"
    Cleaner(service).run_once()
    assert status_of(service, rid) == "revoke_failed"
    local.fail_at = None
    Cleaner(service).run_once()
    assert status_of(service, rid) == "revoked"
    assert local.owned(rid) == []


def test_cleanup_skips_when_lock_held(service):
    with psycopg.connect(service.db.dsn, autocommit=True) as conn:
        conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_CLEANUP,))
        try:
            assert Cleaner(service).run_once()["skipped"] is True
        finally:
            conn.execute("SELECT pg_advisory_unlock(%s)", (LOCK_CLEANUP,))


# ------------------------------------------------------------------ audit
def test_audit_is_append_only(client, service):
    submit(client)
    with pytest.raises(psycopg.Error):
        with service.db.tx() as conn:
            conn.execute("UPDATE audit_log SET actor='x'")
    with pytest.raises(psycopg.Error):
        with service.db.tx() as conn:
            conn.execute("DELETE FROM audit_log")


def test_audit_records_full_lifecycle(client, service):
    rid = approved_request(client, service)
    download(client, make_link(client, rid))
    rows = [a for a in service.recent_audit() if a["request_id"] == rid]
    actions = {a["action"] for a in rows}
    assert {"request_created", "approved", "link_created", "downloaded"} <= actions
    dl = next(a for a in rows if a["action"] == "downloaded")
    assert dl["requester_email"] == DEV and dl["approver"] == ADMIN
    assert dl["cluster"] == "fsel-local" and dl["namespace"] == "team-a" and dl["role"] == "view"
    assert dl["downloaded_at"] is not None and dl["token_expires_at"] is not None
