"""Danh mục namespace dev được xin, đọc từ LABEL trên namespace (không còn ConfigMap whitelist).

Admin mở một namespace bằng tay:
    kubectl label ns <ns> kubeconfig-generator/enabled=true
- `true`      : dev xin được.
- `draining`  : ngừng cấp mới; job dọn thu hồi mọi quyền đã cấp ở namespace đó. Gỡ label sau khi thu hồi xong.
- không label : tắt.
Annotation `kubeconfig-generator/role` chọn ClusterRole (mặc định `view`), chỉ nhận giá trị trong
ALLOWED_CLUSTER_ROLES.

Cùng label đó, Kyverno (deploy/kyverno/) sinh RoleBinding cho SA của tool trong namespace. Không có
RoleBinding thì tool không cấp được gì, nên label là cổng quyết định. Policy Kyverno chặn người không phải
admin sửa label, và loại cứng namespace hệ thống. App vẫn tự lọc blacklist thêm một lớp.

Danh mục được cache NAMESPACE_REFRESH (mặc định 1 phút). Lúc duyệt và lúc tải, app hỏi lại cluster
ngay (fresh=True) để quyết định trên trạng thái mới nhất. Gọi cluster lỗi thì giữ bản cũ và ghi log.
"""
from __future__ import annotations

import logging
import re
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from .config import Settings
from .k8s import NS_STATE_DRAINING, NS_STATE_ENABLED, NS_STATES, ClusterOps, LabeledNamespace

log = logging.getLogger(__name__)

_NS_RE = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")
DEFAULT_ROLE = "view"
RETRY_AFTER_ERROR_SECONDS = 10.0


@dataclass(frozen=True, order=True)
class Grant:
    cluster: str
    namespace: str
    role: str = DEFAULT_ROLE
    state: str = NS_STATE_ENABLED

    @property
    def enabled(self) -> bool:
        return self.state == NS_STATE_ENABLED


def namespace_forbidden(namespace: str, settings: Settings) -> bool:
    ns = (namespace or "").strip().lower()
    if ns in settings.forbidden_namespaces:
        return True
    return any(sub in ns for sub in settings.forbidden_substrings)


def parse_labeled(cluster: str, items: list[LabeledNamespace], settings: Settings) -> list[Grant]:
    """Lọc namespace có label: bỏ tên lạ, namespace cấm, giá trị label lạ, role không cho phép."""
    out: dict[str, Grant] = {}
    for item in items:
        namespace = (item.name or "").strip().lower()
        if not _NS_RE.match(namespace):
            log.warning("label namespace: tên %r không hợp lệ (cluster %s)", namespace, cluster)
            continue
        if namespace_forbidden(namespace, settings):
            log.warning("label namespace: %s/%s nằm trong danh sách cấm, bỏ qua", cluster, namespace)
            continue
        state = (item.state or "").strip()
        if state not in NS_STATES:
            log.warning("label namespace: %s/%s có giá trị %r không hợp lệ, bỏ qua", cluster, namespace, state)
            continue
        role = (item.role or DEFAULT_ROLE).strip() or DEFAULT_ROLE
        if role not in settings.allowed_cluster_roles:
            log.warning("label namespace: %s/%s xin role %r ngoài ALLOWED_CLUSTER_ROLES, bỏ qua",
                        cluster, namespace, role)
            continue
        out[namespace] = Grant(cluster, namespace, role, state)
    return sorted(out.values())


class NamespaceCatalog:
    def __init__(self, clusters: dict[str, ClusterOps], settings: Settings,
                 clock: Callable[[], float] = time.monotonic):
        self.clusters = clusters
        self.settings = settings
        self.ttl = settings.namespace_refresh_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._grants: dict[str, list[Grant]] = {}
        self._loaded_at: dict[str, float] = {}
        self.last_error: dict[str, str] = {}

    # ------------------------------------------------------------ nạp từ cluster
    def _refresh_cluster(self, name: str, force: bool) -> None:
        now = self._clock()
        loaded = self._loaded_at.get(name)
        if not force and loaded is not None and now - loaded < self.ttl:
            return
        with self._lock:
            loaded = self._loaded_at.get(name)
            if not force and loaded is not None and self._clock() - loaded < self.ttl:
                return
            try:
                items = self.clusters[name].list_labeled_namespaces()
            except Exception as exc:  # noqa: BLE001
                # Giữ bản cũ, thử lại sau tối đa 10 giây (không dội API server khi cluster đang lỗi)
                self.last_error[name] = str(exc) or type(exc).__name__
                log.warning("Không đọc được label namespace trên %s, giữ danh mục cũ: %s",
                            name, self.last_error[name])
                self._loaded_at[name] = self._clock() - self.ttl + min(self.ttl, RETRY_AFTER_ERROR_SECONDS)
                return
            self._grants[name] = parse_labeled(name, items, self.settings)
            self._loaded_at[name] = self._clock()
            self.last_error.pop(name, None)

    def refresh(self, force: bool = False, cluster: str | None = None) -> None:
        for name in ([cluster] if cluster else list(self.clusters)):
            if name in self.clusters:
                self._refresh_cluster(name, force)

    def _all(self) -> list[Grant]:
        self.refresh()
        out = [g for name in self.clusters for g in self._grants.get(name, [])]
        # Kiểm lại blacklist lúc dùng (phòng khi cấu hình cấm đổi mà cache chưa nạp lại)
        return sorted(g for g in out if not namespace_forbidden(g.namespace, self.settings))

    # ------------------------------------------------------------ tra cứu
    def grants(self) -> list[Grant]:
        """Namespace dev xin được (label = true)."""
        return [g for g in self._all() if g.enabled]

    def lookup(self, cluster: str, namespace: str, fresh: bool = False) -> Grant | None:
        """Trạng thái hiện tại của namespace (true hoặc draining), None nếu không mở."""
        if cluster not in self.clusters:
            return None
        if fresh:
            self.refresh(force=True, cluster=cluster)
        for g in self._all():
            if g.cluster == cluster and g.namespace == namespace:
                return g
        return None

    def find(self, cluster: str, namespace: str, fresh: bool = False) -> Grant | None:
        """Grant nếu namespace đang cho xin (label = true)."""
        g = self.lookup(cluster, namespace, fresh=fresh)
        return g if g is not None and g.enabled else None

    def draining(self) -> list[Grant]:
        return [g for g in self._all() if g.state == NS_STATE_DRAINING]

    def namespaces_by_cluster(self) -> dict[str, list[str]]:
        """Namespace còn label (true + draining): nơi tool còn quyền, dùng cho job quét tài nguyên mồ côi."""
        out: dict[str, set[str]] = {}
        for g in self._all():
            out.setdefault(g.cluster, set()).add(g.namespace)
        return {c: sorted(v) for c, v in out.items()}
