"""Nghiệm thu trên cluster thật (mặc định fsel-local). Tạo SA/RoleBinding thật trong namespace test.

Biến môi trường:
    KCG_TEST_KUBECONFIG   kubeconfig của SA tool (hoặc admin) trên cluster test
    KCG_TEST_CLUSTER      tên cluster (mặc định fsel-local)
    KCG_TEST_NS_A         namespace được cấp
    KCG_TEST_NS_B         namespace khác, để kiểm tra Forbidden
Chạy:  pytest -m cluster            (bỏ qua test chờ token hết hạn)
       pytest -m "cluster and slow" (chờ ~11 phút)
"""
from __future__ import annotations

import os
import random
import time
from datetime import datetime, timezone

import pytest

from app.k8s import KubeCluster, labels_for
from app.kubeconfig import build_kubeconfig

pytestmark = pytest.mark.cluster

KC = os.environ.get("KCG_TEST_KUBECONFIG")
NS_A = os.environ.get("KCG_TEST_NS_A")
NS_B = os.environ.get("KCG_TEST_NS_B")
CLUSTER = os.environ.get("KCG_TEST_CLUSTER", "fsel-local")
INSTANCE = "pytest"
EMAIL = "kcg-test@atlantic.edu.vn"

if not (KC and NS_A and NS_B):
    pytest.skip("Thiếu KCG_TEST_KUBECONFIG / KCG_TEST_NS_A / KCG_TEST_NS_B", allow_module_level=True)


@pytest.fixture(scope="module")
def cluster():
    return KubeCluster(CLUSTER, KC)


@pytest.fixture
def issued(cluster, tmp_path):
    rid = random.randint(900_000_000, 999_999_999)
    tok = cluster.issue(request_id=rid, email=EMAIL, namespace=NS_A, role="view",
                        expiration_seconds=600, instance=INSTANCE)
    path = tmp_path / "dev.kubeconfig"
    path.write_text(build_kubeconfig(cluster_name=CLUSTER, endpoint=cluster.endpoint, namespace=NS_A,
                                     user_name=tok.sa_name, token=tok.token), encoding="utf-8")
    yield rid, tok, str(path)
    cluster.delete_for_request(request_id=rid, namespace=NS_A, instance=INSTANCE)
    path.unlink(missing_ok=True)


def dev_core(path):
    from kubernetes import client, config

    return client.CoreV1Api(config.new_client_from_config(config_file=path))


def status_of(fn):
    from kubernetes.client.exceptions import ApiException

    try:
        fn()
        return 200
    except ApiException as exc:
        return exc.status


def test_get_pods_in_a_forbidden_in_b(issued):
    _, _, path = issued
    core = dev_core(path)
    assert status_of(lambda: core.list_namespaced_pod(NS_A)) == 200
    assert status_of(lambda: core.list_namespaced_pod(NS_B)) == 403


def test_view_cannot_read_secrets_or_write(issued):
    from kubernetes import client

    _, _, path = issued
    core = dev_core(path)
    assert status_of(lambda: core.list_namespaced_secret(NS_A)) == 403
    cm = client.V1ConfigMap(metadata=client.V1ObjectMeta(name="kcg-should-fail"))
    assert status_of(lambda: core.create_namespaced_config_map(NS_A, cm)) == 403


def test_token_expiry_from_tokenrequest(issued):
    _, tok, _ = issued
    left = (tok.expires_at - datetime.now(timezone.utc)).total_seconds()
    assert 500 < left <= 600


def test_revoke_invalidates_token(cluster, issued):
    rid, _, path = issued
    core = dev_core(path)
    assert status_of(lambda: core.list_namespaced_pod(NS_A)) == 200
    assert cluster.delete_for_request(request_id=rid, namespace=NS_A, instance=INSTANCE) == 2
    deadline = time.time() + 30
    code = None
    while time.time() < deadline:
        code = status_of(lambda: core.list_namespaced_pod(NS_A))
        if code == 401:
            break
        time.sleep(2)
    assert code == 401


def test_delete_only_touches_labelled(cluster):
    from kubernetes import client

    decoy = f"kcg-decoy-{random.randint(1000, 9999)}"
    cluster.core.create_namespaced_service_account(NS_A, client.V1ServiceAccount(
        metadata=client.V1ObjectMeta(name=decoy, labels={"kubeconfig-generator/request-id": "1"})))
    try:
        rid = random.randint(900_000_000, 999_999_999)
        cluster.issue(request_id=rid, email=EMAIL, namespace=NS_A, role="view", expiration_seconds=600,
                      instance=INSTANCE)
        assert rid in cluster.list_owned_request_ids(namespace=NS_A, instance=INSTANCE)
        assert cluster.delete_for_request(request_id=rid, namespace=NS_A, instance=INSTANCE) == 2
        names = [sa.metadata.name for sa in cluster.core.list_namespaced_service_account(NS_A).items]
        assert decoy in names
    finally:
        cluster.core.delete_namespaced_service_account(decoy, NS_A)


def test_labels_on_created_objects(cluster, issued):
    rid, tok, _ = issued
    sa = cluster.core.read_namespaced_service_account(tok.sa_name, NS_A)
    rb = cluster.rbac.read_namespaced_role_binding(tok.sa_name, NS_A)
    expected = labels_for(rid, EMAIL, INSTANCE)
    assert sa.metadata.labels == expected
    assert rb.metadata.labels == expected
    assert rb.role_ref.kind == "ClusterRole" and rb.role_ref.name == "view"


@pytest.mark.slow
def test_expired_token_rejected(issued):
    _, tok, path = issued
    core = dev_core(path)
    wait = (tok.expires_at - datetime.now(timezone.utc)).total_seconds()
    time.sleep(max(0, wait) + 15)
    assert status_of(lambda: core.list_namespaced_pod(NS_A)) == 401
