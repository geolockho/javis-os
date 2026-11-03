"""Dựng file kubeconfig cho dev. Chỉ tạo trong bộ nhớ, không lưu."""
from __future__ import annotations

import yaml

from .k8s import ClusterEndpoint


def build_kubeconfig(*, cluster_name: str, endpoint: ClusterEndpoint, namespace: str,
                     user_name: str, token: str) -> str:
    cluster: dict = {"server": endpoint.server}
    if endpoint.ca_data:
        cluster["certificate-authority-data"] = endpoint.ca_data
    elif endpoint.insecure_skip_tls_verify:
        cluster["insecure-skip-tls-verify"] = True
    context_name = f"{cluster_name}-{namespace}"
    doc = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": [{"name": cluster_name, "cluster": cluster}],
        "users": [{"name": user_name, "user": {"token": token}}],
        "contexts": [{
            "name": context_name,
            "context": {"cluster": cluster_name, "user": user_name, "namespace": namespace},
        }],
        "current-context": context_name,
        "preferences": {},
    }
    return yaml.safe_dump(doc, sort_keys=False)


def kubeconfig_filename(cluster_name: str, namespace: str) -> str:
    return f"kubeconfig-{cluster_name}-{namespace}.yaml"
