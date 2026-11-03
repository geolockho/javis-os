#!/usr/bin/env bash
# Dựng kubeconfig cho SA của tool (sau khi đã apply deploy/rbac/tool.yaml lên cluster).
# Dùng context admin của bạn để đọc token; file ra nằm trong secrets/ (đã .gitignore).
#
#   ./scripts/make_tool_kubeconfig.sh <context-admin> <tên-cluster> > secrets/<tên-cluster>.yaml
set -euo pipefail

CTX="${1:?context admin}"
NAME="${2:?tên cluster, vd fsel-prod}"
NS=kube-public
SECRET=kubeconfig-generator-token

SERVER=$(kubectl --context "$CTX" config view --minify -o jsonpath='{.clusters[0].cluster.server}')
CA=$(kubectl --context "$CTX" -n "$NS" get secret "$SECRET" -o jsonpath='{.data.ca\.crt}')
TOKEN=$(kubectl --context "$CTX" -n "$NS" get secret "$SECRET" -o jsonpath='{.data.token}' | base64 -d)

cat <<EOF
apiVersion: v1
kind: Config
clusters:
- name: ${NAME}
  cluster:
    server: ${SERVER}
    certificate-authority-data: ${CA}
users:
- name: kubeconfig-generator
  user:
    token: ${TOKEN}
contexts:
- name: ${NAME}
  context:
    cluster: ${NAME}
    user: kubeconfig-generator
current-context: ${NAME}
EOF
