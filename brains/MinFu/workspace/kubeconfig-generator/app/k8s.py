"""Thao tác Kubernetes: tạo/xoá SA + RoleBinding theo label, sinh token bằng TokenRequest.

Quy tắc an toàn:
- Chỉ tạo SA và RoleBinding tới ClusterRole đã cho phép. Không tạo Role/ClusterRole/ClusterRoleBinding.
- Xoá luôn chọn theo label (managed-by + instance + request-id), kiểm lại label trên từng object
  trước khi xoá. Không bao giờ xoá theo tên đoán ra.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import os
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

import yaml

log = logging.getLogger(__name__)

LABEL_MANAGED_BY = "app.kubernetes.io/managed-by"
MANAGED_BY_VALUE = "kubeconfig-generator"
LABEL_REQUEST_ID = "kubeconfig-generator/request-id"
LABEL_REQUESTER = "kubeconfig-generator/requester"
LABEL_INSTANCE = "kubeconfig-generator/instance"
ANN_REQUESTER_EMAIL = "kubeconfig-generator/requester-email"

# Label/annotation trên NAMESPACE do admin gắn tay. Kyverno sinh RoleBinding cho tool theo label này
# (deploy/kyverno/), app đọc cùng label để biết namespace nào cho xin.
LABEL_NS_ENABLED = "kubeconfig-generator/enabled"
NS_STATE_ENABLED = "true"        # dev xin được
NS_STATE_DRAINING = "draining"   # ngừng cấp mới, job dọn thu hồi quyền đã cấp
NS_STATES = (NS_STATE_ENABLED, NS_STATE_DRAINING)
ANN_NS_ROLE = "kubeconfig-generator/role"   # ClusterRole cấp cho dev, mặc định "view"


class ClusterError(Exception):
    """Lỗi khi gọi API server (đã che token)."""


@dataclass(frozen=True)
class LabeledNamespace:
    name: str
    state: str               # giá trị label kubeconfig-generator/enabled
    role: str | None = None  # annotation kubeconfig-generator/role (None = mặc định)


@dataclass(frozen=True)
class IssuedToken:
    sa_name: str
    token: str
    expires_at: datetime

    def __repr__(self) -> str:  # không để token lọt ra log qua repr
        return f"IssuedToken(sa_name={self.sa_name!r}, expires_at={self.expires_at!r}, token=[REDACTED])"


@dataclass(frozen=True)
class ClusterEndpoint:
    server: str
    ca_data: str | None          # base64, như trong kubeconfig
    insecure_skip_tls_verify: bool = False


def requester_label(email: str) -> str:
    """Email có '@' nên không làm giá trị label được: dùng hash."""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()[:16]


def sa_name_for(email: str) -> str:
    local = email.split("@", 1)[0].lower()
    local = re.sub(r"[^a-z0-9-]+", "-", local).strip("-") or "user"
    local = local[:40].rstrip("-")
    return f"dev-{local}-{secrets.token_hex(3)}"


def labels_for(request_id: int, email: str, instance: str) -> dict[str, str]:
    return {
        LABEL_MANAGED_BY: MANAGED_BY_VALUE,
        LABEL_INSTANCE: instance,
        LABEL_REQUEST_ID: str(request_id),
        LABEL_REQUESTER: requester_label(email),
    }


def selector_for(request_id: int | None, instance: str) -> str:
    parts = [f"{LABEL_MANAGED_BY}={MANAGED_BY_VALUE}", f"{LABEL_INSTANCE}={instance}"]
    if request_id is not None:
        parts.append(f"{LABEL_REQUEST_ID}={request_id}")
    return ",".join(parts)


def owned_by(labels: dict | None, request_id: int | None, instance: str) -> bool:
    labels = labels or {}
    if labels.get(LABEL_MANAGED_BY) != MANAGED_BY_VALUE or labels.get(LABEL_INSTANCE) != instance:
        return False
    return request_id is None or labels.get(LABEL_REQUEST_ID) == str(request_id)


class ClusterOps(Protocol):
    name: str
    endpoint: ClusterEndpoint

    def namespace_exists(self, namespace: str) -> bool: ...

    def list_labeled_namespaces(self) -> list[LabeledNamespace]: ...

    def issue(self, *, request_id: int, email: str, namespace: str, role: str,
              expiration_seconds: int, instance: str) -> IssuedToken: ...

    def delete_for_request(self, *, request_id: int, namespace: str, instance: str) -> int: ...

    def list_owned_request_ids(self, *, namespace: str, instance: str) -> set[int]: ...


def read_endpoint(kubeconfig_path: str) -> ClusterEndpoint:
    """Lấy server URL và CA của cluster trong current-context của kubeconfig admin."""
    with open(kubeconfig_path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    ctx_name = cfg.get("current-context")
    contexts = {c["name"]: c["context"] for c in cfg.get("contexts", [])}
    clusters = {c["name"]: c["cluster"] for c in cfg.get("clusters", [])}
    if ctx_name not in contexts:
        raise ClusterError(f"{kubeconfig_path}: không có current-context hợp lệ")
    cluster = clusters.get(contexts[ctx_name].get("cluster"))
    if not cluster or not cluster.get("server"):
        raise ClusterError(f"{kubeconfig_path}: context {ctx_name} không trỏ tới cluster có server")
    ca_data = cluster.get("certificate-authority-data")
    if not ca_data and cluster.get("certificate-authority"):
        ca_path = cluster["certificate-authority"]
        if not os.path.isabs(ca_path):
            ca_path = os.path.join(os.path.dirname(kubeconfig_path), ca_path)
        with open(ca_path, "rb") as fh:
            ca_data = base64.b64encode(fh.read()).decode()
    insecure = bool(cluster.get("insecure-skip-tls-verify", False))
    if not ca_data and not insecure:
        raise ClusterError(f"{kubeconfig_path}: thiếu CA của cluster")
    return ClusterEndpoint(server=cluster["server"], ca_data=ca_data, insecure_skip_tls_verify=insecure)


def _api_error(exc: Exception) -> ClusterError:
    status = getattr(exc, "status", None)
    reason = getattr(exc, "reason", None) or type(exc).__name__
    return ClusterError(f"API server lỗi: {status} {reason}".strip())


class KubeCluster:
    """Một cluster thật, mỗi cluster một ApiClient riêng."""

    def __init__(self, name: str, kubeconfig_path: str):
        from kubernetes import client, config

        self.name = name
        self.endpoint = read_endpoint(kubeconfig_path)
        api_client = config.new_client_from_config(config_file=kubeconfig_path)
        self.core = client.CoreV1Api(api_client)
        self.rbac = client.RbacAuthorizationV1Api(api_client)
        self._client = client
        if self.endpoint.insecure_skip_tls_verify:
            log.warning("Cluster %s: kubeconfig admin bật insecure-skip-tls-verify, kubeconfig dev sẽ kế thừa", name)

    def namespace_exists(self, namespace: str) -> bool:
        from kubernetes.client.exceptions import ApiException

        try:
            self.core.read_namespace(namespace)
            return True
        except ApiException as exc:
            if exc.status == 404:
                return False
            raise _api_error(exc) from None

    def list_labeled_namespaces(self) -> list[LabeledNamespace]:
        """Namespace có label kubeconfig-generator/enabled=true|draining (cần quyền list namespaces)."""
        from kubernetes.client.exceptions import ApiException

        selector = f"{LABEL_NS_ENABLED} in ({','.join(NS_STATES)})"
        try:
            items = self.core.list_namespace(label_selector=selector, _request_timeout=10).items
        except ApiException as exc:
            raise _api_error(exc) from None
        out = []
        for ns in items:
            labels = ns.metadata.labels or {}
            annotations = ns.metadata.annotations or {}
            out.append(LabeledNamespace(name=ns.metadata.name, state=labels.get(LABEL_NS_ENABLED, ""),
                                        role=annotations.get(ANN_NS_ROLE)))
        return out

    def issue(self, *, request_id: int, email: str, namespace: str, role: str,
              expiration_seconds: int, instance: str) -> IssuedToken:
        from kubernetes.client.exceptions import ApiException

        c = self._client
        labels = labels_for(request_id, email, instance)
        annotations = {ANN_REQUESTER_EMAIL: email}
        name = sa_name_for(email)
        try:
            self.core.create_namespaced_service_account(
                namespace,
                c.V1ServiceAccount(
                    metadata=c.V1ObjectMeta(name=name, labels=labels, annotations=annotations),
                    automount_service_account_token=False,
                ),
            )
            self.rbac.create_namespaced_role_binding(
                namespace,
                c.V1RoleBinding(
                    metadata=c.V1ObjectMeta(name=name, labels=labels, annotations=annotations),
                    role_ref=c.V1RoleRef(api_group="rbac.authorization.k8s.io", kind="ClusterRole", name=role),
                    subjects=[c.RbacV1Subject(kind="ServiceAccount", name=name, namespace=namespace)],
                ),
            )
            resp = self.core.create_namespaced_service_account_token(
                name,
                namespace,
                c.AuthenticationV1TokenRequest(
                    spec=c.V1TokenRequestSpec(audiences=[], expiration_seconds=expiration_seconds)
                ),
            )
        except ApiException as exc:
            raise _api_error(exc) from None
        expires = resp.status.expiration_timestamp
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return IssuedToken(sa_name=name, token=resp.status.token, expires_at=expires)

    def delete_for_request(self, *, request_id: int, namespace: str, instance: str) -> int:
        from kubernetes.client.exceptions import ApiException

        selector = selector_for(request_id, instance)
        deleted = 0
        try:
            rbs = self.rbac.list_namespaced_role_binding(namespace, label_selector=selector).items
            for rb in rbs:
                if not owned_by(rb.metadata.labels, request_id, instance):
                    continue
                try:
                    self.rbac.delete_namespaced_role_binding(rb.metadata.name, namespace)
                    deleted += 1
                except ApiException as exc:
                    if exc.status != 404:
                        raise
            sas = self.core.list_namespaced_service_account(namespace, label_selector=selector).items
            for sa in sas:
                if not owned_by(sa.metadata.labels, request_id, instance):
                    continue
                try:
                    self.core.delete_namespaced_service_account(sa.metadata.name, namespace)
                    deleted += 1
                except ApiException as exc:
                    if exc.status != 404:
                        raise
        except ApiException as exc:
            raise _api_error(exc) from None
        return deleted

    def list_owned_request_ids(self, *, namespace: str, instance: str) -> set[int]:
        from kubernetes.client.exceptions import ApiException

        selector = selector_for(None, instance)
        ids: set[int] = set()
        try:
            items = list(self.core.list_namespaced_service_account(namespace, label_selector=selector).items)
            items += list(self.rbac.list_namespaced_role_binding(namespace, label_selector=selector).items)
        except ApiException as exc:
            raise _api_error(exc) from None
        for obj in items:
            labels = obj.metadata.labels or {}
            if owned_by(labels, None, instance):
                try:
                    ids.add(int(labels.get(LABEL_REQUEST_ID, "")))
                except ValueError:
                    continue
        return ids


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
