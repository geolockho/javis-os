"""Test không cần DB hay cluster."""
from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

from app.config import ConfigError, load_settings, parse_duration
from app.catalog import Grant, namespace_forbidden
from app.k8s import (LABEL_INSTANCE, LABEL_MANAGED_BY, LABEL_REQUEST_ID, ClusterEndpoint, IssuedToken,
                     labels_for, owned_by, requester_label, sa_name_for, selector_for)
from app.kubeconfig import build_kubeconfig
from app.logging_redact import REDACTED, RedactFilter, redact
from app.ratelimit import TokenBucket

from .conftest import ADMIN, ADMIN2, FAKE_JWT, base_env


# ------------------------------------------------------------------ config
def test_parse_duration():
    assert parse_duration("10m") == 600
    assert parse_duration("24h") == 86400
    assert parse_duration("90d") == 90 * 86400
    with pytest.raises(ConfigError):
        parse_duration("1 month")


def test_expiration_over_max_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_settings(base_env(tmp_path, EXPIRATION_OPTIONS="1d,120d", MAX_EXPIRATION="90d"))


def test_expiration_under_600s_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_settings(base_env(tmp_path, EXPIRATION_OPTIONS="5m"))


def test_admin_match_exact_case_insensitive(settings):
    assert settings.is_admin(ADMIN)
    assert settings.is_admin(ADMIN.upper())
    assert settings.is_admin(ADMIN2)            # cấu hình viết hoa vẫn khớp
    assert not settings.is_admin("x" + ADMIN)
    assert not settings.is_admin(ADMIN + ".evil")
    assert not settings.is_admin("")


def test_default_admin(tmp_path):
    env = base_env(tmp_path)
    del env["ADMIN_EMAILS"]
    assert load_settings(env).admin_emails == frozenset({"hophu@atlantic.edu.vn"})


def test_forbidden_list_cannot_be_removed(tmp_path):
    s = load_settings(base_env(tmp_path, FORBIDDEN_NAMESPACES="extra"))
    for ns in ("cd", "haproxy", "rabbitmq", "redis", "kyverno", "argocd", "fsel-internal-tools",
               "kube-system", "my-kube-ns", "extra"):
        assert namespace_forbidden(ns, s), ns
    assert not namespace_forbidden("team-a", s)


# ------------------------------------------------------------------ danh mục namespace (label)
def test_catalog_from_labels_drops_forbidden(catalog):
    assert catalog.grants() == sorted([
        Grant("fsel-local", "team-a", "view"),
        Grant("fsel-local", "team-b", "view"),
        Grant("fsel-prod", "team-a", "view"),
    ])


def test_catalog_find(catalog):
    assert catalog.find("fsel-local", "team-a")
    assert catalog.find("fsel-local", "team-b")
    assert catalog.find("fsel-prod", "team-b") is None      # chỉ có label ở cluster khác
    assert catalog.find("fsel-local", "team-c") is None     # có trên cluster, không có label
    assert catalog.find("fsel-local", "redis") is None      # có label nhưng bị cấm
    assert catalog.find("unknown-cluster", "team-a") is None
    assert catalog.namespaces_by_cluster() == {"fsel-local": ["team-a", "team-b"], "fsel-prod": ["team-a"]}


def test_parse_labeled_filters(settings):
    from app.catalog import parse_labeled
    from app.k8s import LabeledNamespace as L

    grants = parse_labeled("fsel-local", [
        L("ok", "true"),
        L("drain", "draining"),
        L("bad-value", "false"),           # giá trị lạ
        L("admin-role", "true", "admin"),  # role ngoài ALLOWED_CLUSTER_ROLES
        L("Bad_Name", "true"),             # tên không hợp lệ
        L("kyverno", "true"),              # namespace quyền cao, cấm cứng
        L("argocd", "true"),
        L("fsel-internal-tools", "true"),
        L("my-kube-ns", "true"),
    ], settings)
    assert grants == [Grant("fsel-local", "drain", "view", "draining"), Grant("fsel-local", "ok", "view", "true")]


def test_draining_not_requestable_but_swept(catalog, clusters):
    clusters["fsel-local"].set_label("team-b", "draining")
    catalog.refresh(force=True)
    assert catalog.find("fsel-local", "team-b") is None
    assert catalog.lookup("fsel-local", "team-b").state == "draining"
    assert [g.namespace for g in catalog.draining()] == ["team-b"]
    assert "team-b" in catalog.namespaces_by_cluster()["fsel-local"]       # job dọn vẫn quét
    assert ("fsel-local", "team-b") not in {(g.cluster, g.namespace) for g in catalog.grants()}


def test_catalog_cache_and_fresh(catalog, clusters):
    local = clusters["fsel-local"]
    catalog.grants()
    calls = local.list_calls
    local.set_label("team-c", "true")
    catalog.grants()
    assert local.list_calls == calls                       # còn trong cache, không gọi lại cluster
    assert catalog.find("fsel-local", "team-c") is None
    assert catalog.find("fsel-local", "team-c", fresh=True) is not None   # fresh hỏi lại ngay
    local.set_label("team-c", None)
    assert catalog.find("fsel-local", "team-c", fresh=True) is None


def test_catalog_cache_expires(settings, clusters):
    from app.catalog import NamespaceCatalog

    now = [1000.0]
    cat = NamespaceCatalog(clusters, settings, clock=lambda: now[0])
    assert cat.find("fsel-local", "team-c") is None
    clusters["fsel-local"].set_label("team-c", "true")
    now[0] += settings.namespace_refresh_seconds + 1
    assert cat.find("fsel-local", "team-c") is not None


def test_catalog_cluster_error_keeps_previous(catalog, clusters):
    before = catalog.grants()
    clusters["fsel-local"].fail_at = "list"
    catalog.refresh(force=True)
    assert catalog.grants() == before
    assert "fsel-local" in catalog.last_error
    clusters["fsel-local"].fail_at = None
    catalog.refresh(force=True)
    assert "fsel-local" not in catalog.last_error


def test_catalog_never_loaded_is_empty(settings, clusters):
    from app.catalog import NamespaceCatalog

    clusters["fsel-local"].fail_at = "list"
    cat = NamespaceCatalog(clusters, settings)
    assert all(g.cluster != "fsel-local" for g in cat.grants())


# ------------------------------------------------------------------ manifest RBAC / Kyverno
DEPLOY = Path(__file__).resolve().parents[1] / "deploy"


def _docs(path: Path) -> list[dict]:
    return [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d]


def test_tool_rbac_has_no_rolebinding_or_namespace():
    docs = _docs(DEPLOY / "rbac" / "tool.yaml")
    kinds = [d["kind"] for d in docs]
    assert "Namespace" not in kinds                 # namespace phải có sẵn, không tạo/xoá theo tool
    assert "RoleBinding" not in kinds               # RoleBinding do Kyverno sinh theo label
    issuer = next(d for d in docs if d["kind"] == "ClusterRole" and d["metadata"]["name"] == "kubeconfig-generator-issuer")
    bind = [r for r in issuer["rules"] if "bind" in r["verbs"]]
    assert bind == [{"apiGroups": ["rbac.authorization.k8s.io"], "resources": ["clusterroles"], "verbs": ["bind"],
                     "resourceNames": ["view"]}]
    # issuer không bao giờ bind bằng ClusterRoleBinding
    crbs = [d for d in docs if d["kind"] == "ClusterRoleBinding"]
    assert all(d["roleRef"]["name"] != "kubeconfig-generator-issuer" for d in crbs)
    reader = next(d for d in docs if d["kind"] == "ClusterRole"
                  and d["metadata"]["name"] == "kubeconfig-generator-namespace-reader")
    assert reader["rules"] == [{"apiGroups": [""], "resources": ["namespaces"], "verbs": ["get", "list"]}]


def test_kyverno_generate_policy():
    from app.config import BASE_FORBIDDEN_NAMESPACES
    from app.k8s import LABEL_NS_ENABLED, NS_STATES

    (policy,) = _docs(DEPLOY / "kyverno" / "10-generate-issuer-rolebinding.yaml")
    assert policy["spec"]["generateExisting"] is True
    (rule,) = policy["spec"]["rules"]
    (expr,) = rule["match"]["any"][0]["resources"]["selector"]["matchExpressions"]
    assert expr == {"key": LABEL_NS_ENABLED, "operator": "In", "values": list(NS_STATES)}
    excluded = set(rule["exclude"]["any"][0]["resources"]["names"])
    assert BASE_FORBIDDEN_NAMESPACES <= excluded and "*kube*" in excluded
    gen = rule["generate"]
    assert gen["synchronize"] is True
    assert gen["kind"] == "RoleBinding" and gen["name"] == "kubeconfig-generator-issuer"
    assert gen["data"]["roleRef"]["name"] == "kubeconfig-generator-issuer"
    assert gen["data"]["subjects"] == [{"kind": "ServiceAccount", "name": "kubeconfig-generator",
                                        "namespace": "kube-public"}]
    # Không gắn label managed-by của tool (label đó dùng để chọn object của dev khi xoá)
    assert "app.kubernetes.io/managed-by" not in gen["data"]["metadata"]["labels"]


def test_kyverno_protect_policy():
    (policy,) = _docs(DEPLOY / "kyverno" / "20-protect-namespace-labels.yaml")
    assert policy["spec"]["validationFailureAction"] == "Enforce"
    rules = {r["name"]: r for r in policy["spec"]["rules"]}
    assert set(rules) == {"only-admins-change", "valid-value", "drain-before-disable"}
    assert rules["only-admins-change"]["exclude"]["any"][0]["clusterRoles"] == ["cluster-admin"]
    # Hai rule còn lại áp cho mọi người, kể cả admin
    assert "exclude" not in rules["valid-value"] and "exclude" not in rules["drain-before-disable"]


def test_kyverno_rbac_bind_only_issuer():
    docs = _docs(DEPLOY / "kyverno" / "00-kyverno-rbac.yaml")
    bg = next(d for d in docs if d["metadata"]["labels"].get("rbac.kyverno.io/aggregate-to-background-controller"))
    bind = [r for r in bg["rules"] if "bind" in r["verbs"]]
    assert bind[0]["resourceNames"] == ["kubeconfig-generator-issuer"]


def test_no_namespace_configmap_left():
    assert not (DEPLOY / "configmap-namespaces.yaml").exists()
    deployment = (DEPLOY / "deployment.yaml").read_text(encoding="utf-8")
    assert "kubeconfig-generator-namespaces" not in deployment


# ------------------------------------------------------------------ k8s helpers
def test_labels_and_selector():
    labels = labels_for(42, "Dev.A@atlantic.edu.vn", "default")
    assert labels[LABEL_MANAGED_BY] == "kubeconfig-generator"
    assert labels[LABEL_REQUEST_ID] == "42"
    assert labels[LABEL_INSTANCE] == "default"
    assert "@" not in "".join(labels.values())
    assert requester_label("dev.a@atlantic.edu.vn") == requester_label("DEV.A@atlantic.edu.vn")
    assert selector_for(42, "default") == (
        "app.kubernetes.io/managed-by=kubeconfig-generator,kubeconfig-generator/instance=default,"
        "kubeconfig-generator/request-id=42")


def test_owned_by_requires_all_labels():
    labels = labels_for(7, "a@b.c", "default")
    assert owned_by(labels, 7, "default")
    assert not owned_by(labels, 8, "default")
    assert not owned_by(labels, 7, "staging")
    assert not owned_by({LABEL_REQUEST_ID: "7"}, 7, "default")   # thiếu managed-by
    assert not owned_by(None, None, "default")


def test_sa_name_is_dns_safe():
    import re

    for email in ("Dev.A@x.y", "nguyen_van+test@x.y", "a" * 80 + "@x.y", "@x.y"):
        name = sa_name_for(email)
        assert re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", name), name
        assert len(name) <= 63
        assert name.startswith("dev-")


def test_issued_token_repr_hides_token():
    from datetime import datetime, timezone

    t = IssuedToken("sa", FAKE_JWT, datetime.now(timezone.utc))
    assert FAKE_JWT not in repr(t)


# ------------------------------------------------------------------ kubeconfig
def _write_admin_kubeconfig(tmp_path, cluster: dict) -> str:
    doc = {
        "apiVersion": "v1", "kind": "Config", "current-context": "tool",
        "contexts": [{"name": "other", "context": {"cluster": "wrong", "user": "u"}},
                     {"name": "tool", "context": {"cluster": "fsel-local", "user": "u"}}],
        "clusters": [{"name": "wrong", "cluster": {"server": "https://wrong:6443", "certificate-authority-data": "X"}},
                     {"name": "fsel-local", "cluster": cluster}],
        "users": [{"name": "u", "user": {"token": "t"}}],
    }
    path = tmp_path / "admin.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return str(path)


def test_read_endpoint_uses_current_context(tmp_path):
    from app.k8s import read_endpoint

    path = _write_admin_kubeconfig(tmp_path, {"server": "https://101.99.7.167:6444",
                                              "certificate-authority-data": "Q0E="})
    ep = read_endpoint(path)
    assert ep.server == "https://101.99.7.167:6444" and ep.ca_data == "Q0E="


def test_read_endpoint_ca_file(tmp_path):
    import base64

    from app.k8s import read_endpoint

    (tmp_path / "ca.crt").write_bytes(b"CERT")
    path = _write_admin_kubeconfig(tmp_path, {"server": "https://x:6443", "certificate-authority": "ca.crt"})
    assert read_endpoint(path).ca_data == base64.b64encode(b"CERT").decode()


def test_read_endpoint_requires_ca(tmp_path):
    from app.k8s import ClusterError, read_endpoint

    path = _write_admin_kubeconfig(tmp_path, {"server": "https://x:6443"})
    with pytest.raises(ClusterError):
        read_endpoint(path)


def test_build_kubeconfig():
    text = build_kubeconfig(cluster_name="fsel-local", endpoint=ClusterEndpoint("https://1.2.3.4:6444", "Q0E="),
                            namespace="team-a", user_name="dev-a-123", token="TOKEN")
    doc = yaml.safe_load(text)
    assert doc["current-context"] == "fsel-local-team-a"
    ctx = doc["contexts"][0]["context"]
    assert ctx["namespace"] == "team-a"
    assert doc["clusters"][0]["cluster"] == {"server": "https://1.2.3.4:6444", "certificate-authority-data": "Q0E="}
    assert doc["users"][0]["user"] == {"token": "TOKEN"}


# ------------------------------------------------------------------ redact
def test_redact_jwt_and_link_token():
    link_token = "A" * 20 + "b-_" + "C" * 20       # 43 ký tự như token_urlsafe(32)
    text = f"token={FAKE_JWT} url=/dl#{link_token} Authorization: Bearer {FAKE_JWT}"
    out = redact(text)
    assert FAKE_JWT not in out
    assert link_token not in out
    assert REDACTED in out


def test_redact_filter_on_logger(caplog):
    lg = logging.getLogger("test.redact")
    lg.addFilter(RedactFilter())
    with caplog.at_level(logging.INFO, logger="test.redact"):
        lg.info("issued %s", FAKE_JWT)
    assert FAKE_JWT not in caplog.text


# ------------------------------------------------------------------ rate limit
def test_token_bucket():
    b = TokenBucket(rate=3, capacity=3)
    assert [b.allow("ip", now=0.0) for _ in range(4)] == [True, True, True, False]
    assert b.allow("ip", now=0.34)               # nạp lại ~1 lượt
    assert b.allow("other", now=0.0)             # mỗi IP một xô
