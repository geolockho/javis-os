"""Đọc cấu hình từ biến môi trường (.env được nạp bởi Docker/K8s, không đọc file .env trong code)."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# Namespace bị cấm cứng. Biến FORBIDDEN_NAMESPACES chỉ THÊM vào, không bỏ bớt được.
# cd, haproxy, rabbitmq, redis theo đặc tả; kyverno, argocd, fsel-internal-tools chứa SA quyền cao (tool tạo được
# token của mọi SA trong namespace được mở). Phải khớp exclude trong deploy/kyverno/10-generate-issuer-rolebinding.yaml.
BASE_FORBIDDEN_NAMESPACES = frozenset({"cd", "haproxy", "rabbitmq", "redis", "kyverno", "argocd",
                                       "fsel-internal-tools"})
BASE_FORBIDDEN_SUBSTRINGS = frozenset({"kube"})

_DURATION_RE = re.compile(r"^\s*(\d+)\s*([mhd])\s*$")
_UNIT_SECONDS = {"m": 60, "h": 3600, "d": 86400}


class ConfigError(ValueError):
    pass


def parse_duration(text: str) -> int:
    """'10m' / '12h' / '30d' -> số giây."""
    m = _DURATION_RE.match(text or "")
    if not m:
        raise ConfigError(f"Thời lượng không hợp lệ: {text!r} (dùng dạng 10m, 12h, 30d)")
    return int(m.group(1)) * _UNIT_SECONDS[m.group(2)]


def format_duration(seconds: int) -> str:
    if seconds % 86400 == 0:
        d = seconds // 86400
        return f"{d} ngày"
    if seconds % 3600 == 0:
        return f"{seconds // 3600} giờ"
    return f"{seconds // 60} phút"


def _csv(value: str | None) -> list[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(env: dict, key: str, default: int) -> int:
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{key} phải là số nguyên") from exc


@dataclass(frozen=True)
class ClusterConfig:
    name: str
    kubeconfig_path: str


@dataclass
class Settings:
    database_url: str
    clusters: dict[str, ClusterConfig]
    admin_emails: frozenset[str]
    public_url: str
    allow_self_approve: bool = False
    slack_webhook_url: str = ""
    claim_window_seconds: int = 24 * 3600
    link_ttl_seconds: int = 15 * 60
    expiration_options: list[int] = field(default_factory=list)
    max_expiration_seconds: int = 90 * 86400
    allowed_cluster_roles: frozenset[str] = frozenset({"view"})
    forbidden_namespaces: frozenset[str] = BASE_FORBIDDEN_NAMESPACES
    forbidden_substrings: frozenset[str] = BASE_FORBIDDEN_SUBSTRINGS
    max_pending_per_user: int = 5
    email_header: str = "X-Forwarded-Email"
    client_ip_header: str = "X-Real-IP"
    rate_limit_per_second: float = 3.0
    link_rate_per_minute: int = 10
    download_rate_per_minute: int = 10
    cleanup_interval_seconds: int = 300
    issuing_stuck_seconds: int = 600
    namespace_refresh_seconds: int = 60
    instance_id: str = "default"
    log_level: str = "INFO"

    @property
    def public_origin(self) -> str:
        m = re.match(r"^(https?://[^/]+)", self.public_url)
        return m.group(1).lower() if m else ""

    def is_admin(self, email: str) -> bool:
        return (email or "").strip().lower() in self.admin_emails


_LABEL_VALUE_RE = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")


def load_settings(env: dict | None = None) -> Settings:
    env = dict(os.environ if env is None else env)

    database_url = env.get("DATABASE_URL", "")
    if not database_url:
        raise ConfigError("Thiếu DATABASE_URL")

    clusters: dict[str, ClusterConfig] = {}
    for name in _csv(env.get("CLUSTERS", "fsel-prod,fsel-local")):
        key = "KUBECONFIG_" + name.upper().replace("-", "_")
        path = env.get(key, "")
        if not path:
            raise ConfigError(f"Thiếu {key} (đường dẫn kubeconfig admin của cluster {name})")
        clusters[name] = ClusterConfig(name=name, kubeconfig_path=path)
    if not clusters:
        raise ConfigError("CLUSTERS rỗng")

    admin_emails = frozenset(e.lower() for e in _csv(env.get("ADMIN_EMAILS", "hophu@atlantic.edu.vn")))

    options_raw = _csv(env.get("EXPIRATION_OPTIONS", "1d,7d,30d,90d"))
    max_exp = parse_duration(env.get("MAX_EXPIRATION", "90d"))
    options = sorted({parse_duration(o) for o in options_raw})
    if not options:
        raise ConfigError("EXPIRATION_OPTIONS rỗng")
    for o in options:
        if o > max_exp:
            raise ConfigError(f"Lựa chọn thời hạn {format_duration(o)} vượt MAX_EXPIRATION")
        if o < 600:
            raise ConfigError("Thời hạn tối thiểu là 10m (TokenRequest không nhận dưới 600 giây)")

    roles = frozenset(_csv(env.get("ALLOWED_CLUSTER_ROLES", "view")))
    if not roles:
        raise ConfigError("ALLOWED_CLUSTER_ROLES rỗng")

    instance_id = env.get("INSTANCE_ID", "default").strip().lower()
    if not _LABEL_VALUE_RE.match(instance_id):
        raise ConfigError("INSTANCE_ID phải là giá trị label hợp lệ (a-z, 0-9, '-')")

    public_url = env.get("PUBLIC_URL", "").rstrip("/")
    if not public_url:
        raise ConfigError("Thiếu PUBLIC_URL (vd https://kubeconfig-generator.fsel.edu.vn)")

    return Settings(
        database_url=database_url,
        clusters=clusters,
        admin_emails=admin_emails,
        public_url=public_url,
        allow_self_approve=_bool(env.get("ALLOW_SELF_APPROVE"), False),
        slack_webhook_url=env.get("SLACK_WEBHOOK_URL", ""),
        claim_window_seconds=parse_duration(env.get("CLAIM_WINDOW", "24h")),
        link_ttl_seconds=parse_duration(env.get("LINK_TTL", "15m")),
        expiration_options=options,
        max_expiration_seconds=max_exp,
        allowed_cluster_roles=roles,
        forbidden_namespaces=BASE_FORBIDDEN_NAMESPACES | frozenset(_csv(env.get("FORBIDDEN_NAMESPACES"))),
        forbidden_substrings=BASE_FORBIDDEN_SUBSTRINGS | frozenset(_csv(env.get("FORBIDDEN_SUBSTRINGS"))),
        max_pending_per_user=_int(env, "MAX_PENDING_PER_USER", 5),
        email_header=env.get("EMAIL_HEADER", "X-Forwarded-Email"),
        client_ip_header=env.get("CLIENT_IP_HEADER", "X-Real-IP"),
        rate_limit_per_second=float(env.get("RATE_LIMIT_PER_SECOND", "3")),
        link_rate_per_minute=_int(env, "LINK_RATE_PER_MINUTE", 10),
        download_rate_per_minute=_int(env, "DOWNLOAD_RATE_PER_MINUTE", 10),
        cleanup_interval_seconds=parse_duration(env.get("CLEANUP_INTERVAL", "5m")),
        issuing_stuck_seconds=parse_duration(env.get("ISSUING_STUCK_AFTER", "10m")),
        # Danh mục namespace đọc từ label trên cluster; NAMESPACES_PATH cũ (ConfigMap) không còn dùng
        namespace_refresh_seconds=parse_duration(env.get("NAMESPACE_REFRESH", "1m")),
        instance_id=instance_id,
        log_level=env.get("LOG_LEVEL", "INFO").upper(),
    )
