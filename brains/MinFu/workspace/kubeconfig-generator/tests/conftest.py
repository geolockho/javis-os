from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timedelta, timezone

import pytest

from app.catalog import NamespaceCatalog
from app.config import load_settings
from app.k8s import (ClusterEndpoint, ClusterError, IssuedToken, LabeledNamespace, labels_for, owned_by,
                     sa_name_for)

ADMIN = "hophu@atlantic.edu.vn"
ADMIN2 = "admin2@atlantic.edu.vn"
DEV = "dev.a@atlantic.edu.vn"
DEV_B = "dev.b@atlantic.edu.vn"

# Label kubeconfig-generator/enabled trên namespace của từng cluster giả: {namespace: (giá trị label, role annotation)}
# team-c tồn tại trên cluster nhưng KHÔNG có label.
NS_LABELS = {
    "fsel-local": {
        "team-a": ("true", None),
        "team-b": ("true", "view"),
        "redis": ("true", None),          # bị cấm, phải bị bỏ dù có label
        "kube-public": ("true", None),    # chứa 'kube', phải bị bỏ
    },
    "fsel-prod": {
        "team-a": ("true", None),
    },
}

# Chuỗi giống JWT để kiểm tra không lọt vào log
FAKE_JWT = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXRva2VuLXNob3VsZC1ub3QtbGVhayJ9.c2lnbmF0dXJlLXNlY3JldA"


def base_env(tmp_path, **overrides) -> dict:
    env = {
        "DATABASE_URL": os.environ.get("TEST_DATABASE_URL", "postgresql://unused/unused"),
        "PUBLIC_URL": "https://kubeconfig-generator.fsel.edu.vn",
        "CLUSTERS": "fsel-prod,fsel-local",
        "KUBECONFIG_FSEL_PROD": "/dev/null",
        "KUBECONFIG_FSEL_LOCAL": "/dev/null",
        "ADMIN_EMAILS": f"{ADMIN}, {ADMIN2.upper()}",
        "EXPIRATION_OPTIONS": "10m,1d,30d,90d",
        "RATE_LIMIT_PER_SECOND": "1000",
        "LINK_RATE_PER_MINUTE": "1000",
        "DOWNLOAD_RATE_PER_MINUTE": "1000",
    }
    env.update(overrides)
    return env


class FakeCluster:
    """Giả lập API server: lưu SA/RoleBinding trong bộ nhớ, có thể gây lỗi giữa chừng."""

    def __init__(self, name: str):
        self.name = name
        self.endpoint = ClusterEndpoint(server=f"https://{name}.example:6443", ca_data="Q0EtREFUQQ==")
        self.objects: list[dict] = []          # {kind, namespace, name, labels}
        self.namespaces = {"team-a", "team-b", "team-c", "redis", "kube-public"}
        self.ns_labels: dict[str, tuple[str, str | None]] = dict(NS_LABELS.get(name, {}))
        self.fail_at: str | None = None        # 'rolebinding' | 'token' | 'delete' | 'list'
        self.issue_delay = 0.0
        self.issue_calls = 0
        self.list_calls = 0
        self.truncate_to: int | None = None
        self._lock = threading.Lock()

    def namespace_exists(self, namespace: str) -> bool:
        return namespace in self.namespaces

    def set_label(self, namespace: str, state: str | None, role: str | None = None) -> None:
        """Giả lập admin `kubectl label ns`: state None = gỡ label."""
        if state is None:
            self.ns_labels.pop(namespace, None)
        else:
            self.namespaces.add(namespace)
            self.ns_labels[namespace] = (state, role)

    def list_labeled_namespaces(self) -> list[LabeledNamespace]:
        self.list_calls += 1
        if self.fail_at == "list":
            raise ClusterError("API server lỗi: 503 unavailable")
        # Giống label selector `in (true,draining)` của API server
        return [LabeledNamespace(ns, state, role) for ns, (state, role) in self.ns_labels.items()
                if state in ("true", "draining")]

    def issue(self, *, request_id, email, namespace, role, expiration_seconds, instance) -> IssuedToken:
        with self._lock:
            self.issue_calls += 1
        labels = labels_for(request_id, email, instance)
        name = sa_name_for(email)
        if self.issue_delay:
            time.sleep(self.issue_delay)
        with self._lock:
            self.objects.append({"kind": "ServiceAccount", "namespace": namespace, "name": name, "labels": labels})
        if self.fail_at == "rolebinding":
            raise ClusterError("API server lỗi: 500 boom")
        with self._lock:
            self.objects.append({"kind": "RoleBinding", "namespace": namespace, "name": name, "labels": labels,
                                 "role": role})
        if self.fail_at == "token":
            raise ClusterError("API server lỗi: 500 boom")
        secs = min(expiration_seconds, self.truncate_to or expiration_seconds)
        return IssuedToken(sa_name=name, token=FAKE_JWT, expires_at=datetime.now(timezone.utc) + timedelta(seconds=secs))

    def delete_for_request(self, *, request_id, namespace, instance) -> int:
        if self.fail_at == "delete":
            raise ClusterError("API server lỗi: 503 unavailable")
        with self._lock:
            keep, gone = [], 0
            for o in self.objects:
                if o["namespace"] == namespace and owned_by(o["labels"], request_id, instance):
                    gone += 1
                else:
                    keep.append(o)
            self.objects = keep
        return gone

    def list_owned_request_ids(self, *, namespace, instance) -> set[int]:
        ids = set()
        for o in self.objects:
            if o["namespace"] == namespace and owned_by(o["labels"], None, instance):
                ids.add(int(o["labels"]["kubeconfig-generator/request-id"]))
        return ids

    def owned(self, request_id: int | None = None) -> list[dict]:
        return [o for o in self.objects
                if owned_by(o["labels"], request_id, "default")]


@pytest.fixture
def settings(tmp_path):
    return load_settings(base_env(tmp_path))


@pytest.fixture
def catalog(settings, clusters):
    return NamespaceCatalog(clusters, settings)


# ------------------------------------------------------------------ DB
@pytest.fixture
def db(settings):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Cần TEST_DATABASE_URL (PostgreSQL dùng riêng cho test, sẽ bị xoá schema public)")
    import psycopg

    from app.db import Database

    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
    database = Database(url, max_size=10)
    database.migrate()
    yield database
    database.close()


@pytest.fixture
def clusters():
    return {"fsel-prod": FakeCluster("fsel-prod"), "fsel-local": FakeCluster("fsel-local")}


@pytest.fixture
def service(settings, db, clusters, catalog):
    from app.service import Service

    return Service(settings, db, clusters, catalog)


@pytest.fixture
def client(settings, service):
    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app(settings, service, start_cleaner=False)
    with TestClient(app, base_url="https://kubeconfig-generator.fsel.edu.vn") as c:
        yield c


def hdr(email: str) -> dict:
    # Cố ý không gửi X-Forwarded-Groups: quyền xin không phụ thuộc group
    return {"X-Forwarded-Email": email, "X-Real-IP": "10.1.2.3"}
