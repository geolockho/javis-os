---
type: source
source_kind: own-note
status: processed
created: 2026-10-07
processed_at: 2026-10-07
wiki_links: ["[[wiki/devops/Kubeconfig ServiceAccount cho FPT FKE]]"]
url: null
original_path: "D:\\private01\\readme\\Create_ServiceAccount_Kubeconfig.md"
original_sha256: a23af52e5d7fb14f049fca2d533f76be2db394d4bdb15481fed0ef37217b50b6
---

# FPT FKE - Long-Lived Admin Kubeconfig using ServiceAccount

## Purpose

FPT FKE kubeconfig được cấp từ Portal/Gardener sử dụng X.509 client certificate có thời hạn ngắn.

Ví dụ:

```text
subject=O=gardener.cloud:project:admins, CN=gardener.cloud:admin:portal-k8s-service
issuer=CN=ca-client-58f8e9ac

notBefore=Sep  3 03:22:11 2026 GMT
notAfter =Sep  4 03:23:11 2026 GMT
```

Sau khoảng 24 giờ:

```bash
kubectl get nodes
```

có thể lỗi:

```text
remote error: tls: expired certificate
```

Mục tiêu:

```text
FPT temporary kubeconfig
        │
        │ bootstrap một lần
        ▼
Kubernetes ServiceAccount
        │
        ├── RBAC
        │
        └── long-lived ServiceAccount token
                    │
                    ▼
             admin kubeconfig
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       kubectl     Lens    jump server
```

Kubeconfig mới không còn phụ thuộc vào client certificate 24h từ FPT.

---

## Architecture

```text
                        FPT FKE
                           │
                           │ Kubernetes API
                           │
           https://api.<cluster>.fke.fptcloud.com
                           ▲
                           │
                    Bearer Token
                           │
                  ServiceAccount
                     fke-admin
                           │
                  ClusterRoleBinding
                           │
                     cluster-admin
                           ▲
                           │
                    admin-kubeconfig
                  ┌────────┼────────┐
                  │        │        │
               kubectl    Lens     Jump
```

Authentication:

```text
Before

kubectl
   │
   │ client certificate (~24h)
   ▼
FKE API


After

kubectl
   │
   │ Authorization: Bearer <SA_TOKEN>
   ▼
FKE API
```

---

## Requirements

Cần có một FPT kubeconfig **vẫn còn hiệu lực** để bootstrap ServiceAccount.

Kiểm tra:

```bash
kubectl get nodes
```

Phải thành công.

Kiểm tra context:

```bash
kubectl config current-context
```

Kiểm tra API server:

```bash
kubectl config view --raw --minify \
  -o jsonpath='{.clusters[0].cluster.server}{"\n"}'
```

Ví dụ:

```text
https://api.an4bngw0.prd.m.fke.fptcloud.com
```

---

## 1. Configure variables

```bash
export SA_NAMESPACE=kube-system
export SA_NAME=fke-admin
export SA_SECRET=fke-admin-token

export OUTPUT_KUBECONFIG="$HOME/.kube/fke-admin.yaml"
```

Kiểm tra:

```bash
echo "SA_NAMESPACE=$SA_NAMESPACE"
echo "SA_NAME=$SA_NAME"
echo "SA_SECRET=$SA_SECRET"
echo "OUTPUT_KUBECONFIG=$OUTPUT_KUBECONFIG"
```

---

## 2. Create ServiceAccount

```bash
kubectl -n "$SA_NAMESPACE" create serviceaccount "$SA_NAME"
```

Nếu đã tồn tại:

```bash
kubectl -n "$SA_NAMESPACE" get serviceaccount "$SA_NAME"
```

Expected:

```text
NAME        SECRETS   AGE
fke-admin   0         ...
```

`SECRETS=0` là bình thường trên Kubernetes mới.

Kubernetes >=1.24 không còn tự động tạo long-lived Secret token cho mỗi ServiceAccount.

---

## 3. Grant RBAC

### Option 3A - Full cluster-admin

> Chỉ dùng khi kubeconfig này thực sự cần quyền quản trị toàn cluster.

```bash
kubectl create clusterrolebinding fke-admin-cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount="${SA_NAMESPACE}:${SA_NAME}"
```

Verify:

```bash
kubectl get clusterrolebinding fke-admin-cluster-admin
```

Kiểm tra subject:

```bash
kubectl get clusterrolebinding fke-admin-cluster-admin \
  -o jsonpath='{range .subjects[*]}kind={.kind} namespace={.namespace} name={.name}{"\n"}{end}'
```

Expected:

```text
kind=ServiceAccount namespace=kube-system name=fke-admin
```

`cluster-admin` có toàn quyền trên toàn cluster.

---

## 4. Create long-lived ServiceAccount token

Kubernetes mới không tự động tạo permanent token Secret.

Tạo thủ công:

```bash
cat <<EOF2 | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: ${SA_SECRET}
  namespace: ${SA_NAMESPACE}
  annotations:
    kubernetes.io/service-account.name: ${SA_NAME}
type: kubernetes.io/service-account-token
EOF2
```

Kiểm tra:

```bash
kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET"
```

Expected:

```text
NAME              TYPE                                  DATA
fke-admin-token   kubernetes.io/service-account-token   3
```

Controller sẽ populate:

```text
ca.crt
namespace
token
```

Kiểm tra:

```bash
kubectl -n "$SA_NAMESPACE" describe secret "$SA_SECRET"
```

Expected:

```text
Type: kubernetes.io/service-account-token

Data
====
ca.crt:     ...
namespace:  ...
token:      ...
```

Nếu token chưa xuất hiện ngay:

```bash
until kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
  -o jsonpath='{.data.token}' 2>/dev/null | grep -q .; do
    echo "Waiting for ServiceAccount token..."
    sleep 2
done

echo "Token ready"
```

---

## 5. Extract connection information

### API Server

```bash
SERVER=$(
  kubectl config view --raw --minify \
    -o jsonpath='{.clusters[0].cluster.server}'
)

echo "$SERVER"
```

Ví dụ:

```text
https://api.an4bngw0.prd.m.fke.fptcloud.com
```

### ServiceAccount Token

```bash
TOKEN=$(
  kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
    -o jsonpath='{.data.token}' |
  base64 -d
)
```

Không `echo "$TOKEN"` ra terminal nếu không cần thiết.

Kiểm tra token đã lấy được:

```bash
if [ -n "$TOKEN" ]; then
  echo "TOKEN=OK"
else
  echo "TOKEN=EMPTY"
fi
```

### Cluster CA

Ưu tiên lấy CA trực tiếp từ ServiceAccount Secret:

```bash
kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
  -o jsonpath='{.data.ca\.crt}' |
base64 -d > /tmp/fke-ca.crt
```

Kiểm tra:

```bash
openssl x509 \
  -in /tmp/fke-ca.crt \
  -noout \
  -subject \
  -issuer \
  -dates
```

---

## 6. Create standalone kubeconfig

Tạo directory:

```bash
mkdir -p "$(dirname "$OUTPUT_KUBECONFIG")"
```

Xóa file cũ nếu đang rebuild:

```bash
rm -f "$OUTPUT_KUBECONFIG"
```

Tạo cluster:

```bash
kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  set-cluster fpt-fke \
  --server="$SERVER" \
  --certificate-authority=/tmp/fke-ca.crt \
  --embed-certs=true
```

Tạo credential:

```bash
kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  set-credentials "$SA_NAME" \
  --token="$TOKEN"
```

Tạo context:

```bash
kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  set-context fpt-fke-admin \
  --cluster=fpt-fke \
  --user="$SA_NAME"
```

Set current context:

```bash
kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  use-context fpt-fke-admin
```

Set permission:

```bash
chmod 600 "$OUTPUT_KUBECONFIG"
```

Xóa temporary CA:

```bash
rm -f /tmp/fke-ca.crt
```

---

## 7. Inspect kubeconfig

```bash
kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  view --minify
```

Kubeconfig sẽ có cấu trúc tương tự:

```yaml
apiVersion: v1
kind: Config

clusters:
  - name: fpt-fke
    cluster:
      server: https://api.an4bngw0.prd.m.fke.fptcloud.com
      certificate-authority-data: <CA>

users:
  - name: fke-admin
    user:
      token: <SERVICE_ACCOUNT_TOKEN>

contexts:
  - name: fpt-fke-admin
    context:
      cluster: fpt-fke
      user: fke-admin

current-context: fpt-fke-admin
```

Không còn:

```yaml
client-certificate-data:
client-key-data:
```

---

## 8. Verify authentication

Test bằng kubeconfig mới:

```bash
KUBECONFIG="$OUTPUT_KUBECONFIG" \
kubectl get nodes
```

Kiểm tra API:

```bash
KUBECONFIG="$OUTPUT_KUBECONFIG" \
kubectl get --raw=/version
```

Kiểm tra identity:

```bash
KUBECONFIG="$OUTPUT_KUBECONFIG" \
kubectl auth whoami
```

Expected tương tự:

```text
Username
system:serviceaccount:kube-system:fke-admin
```

Kiểm tra quyền:

```bash
KUBECONFIG="$OUTPUT_KUBECONFIG" \
kubectl auth can-i '*' '*' --all-namespaces
```

Với `cluster-admin`:

```text
yes
```

---

## 9. Verify independence from FPT kubeconfig

Đây là test quan trọng nhất.

FPT kubeconfig ban đầu có thể hết hạn:

```text
client certificate
        │
        └── EXPIRED
```

Nhưng:

```bash
KUBECONFIG="$OUTPUT_KUBECONFIG" \
kubectl get nodes
```

vẫn phải hoạt động.

Flow:

```text
Original FPT kubeconfig
client cert expired
        │
        X

fke-admin.yaml
        │
        │ ServiceAccount Bearer Token
        ▼
    FKE API
        │
        └── OK
```

---

## 10. Use as default kubeconfig

### Linux

Sử dụng tạm:

```bash
export KUBECONFIG="$HOME/.kube/fke-admin.yaml"
```

Verify:

```bash
kubectl config current-context
kubectl get nodes
```

Hoặc dùng theo command:

```bash
kubectl \
  --kubeconfig="$HOME/.kube/fke-admin.yaml" \
  get nodes
```

---

## 11. Use with Lens

Trong Lens:

```text
Catalog
  ↓
Clusters
  ↓
Add Cluster / Add Kubeconfig
  ↓
Select:
fke-admin.yaml
```

Lens sẽ authenticate bằng ServiceAccount Bearer Token thay vì FPT 24-hour client certificate.

---

## 12. Check token type

Decode JWT payload:

```bash
TOKEN=$(
  kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
    -o jsonpath='{.data.token}' |
  base64 -d
)

echo "$TOKEN" |
cut -d. -f2 |
tr '_-' '/+' |
base64 -d 2>/dev/null |
jq
```

Manual ServiceAccount token Secret thông thường sẽ không có:

```json
"exp": ...
```

Trong khi token tạo bằng:

```bash
kubectl create token fke-admin
```

là TokenRequest token và có thời hạn.

Nếu mục tiêu là kubeconfig long-lived, không dùng `kubectl create token` thay cho manual Secret ở README này.

---

## 13. Revoke access

Nếu cần revoke kubeconfig ngay:

```bash
kubectl -n "$SA_NAMESPACE" delete secret "$SA_SECRET"
```

Token trong kubeconfig cũ sẽ không còn sử dụng được.

Verify:

```bash
KUBECONFIG="$OUTPUT_KUBECONFIG" \
kubectl get nodes
```

phải fail authentication.

---

## 14. Rotate token

Xóa Secret cũ:

```bash
kubectl -n "$SA_NAMESPACE" delete secret "$SA_SECRET"
```

Tạo token mới:

```bash
cat <<EOF2 | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: ${SA_SECRET}
  namespace: ${SA_NAMESPACE}
  annotations:
    kubernetes.io/service-account.name: ${SA_NAME}
type: kubernetes.io/service-account-token
EOF2
```

Đợi token:

```bash
until kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
  -o jsonpath='{.data.token}' 2>/dev/null | grep -q .; do
    sleep 2
done
```

Sau đó generate lại kubeconfig.

---

## 15. Remove completely

```bash
kubectl -n "$SA_NAMESPACE" delete secret "$SA_SECRET"

kubectl delete clusterrolebinding \
  fke-admin-cluster-admin

kubectl -n "$SA_NAMESPACE" delete serviceaccount \
  "$SA_NAME"
```

---

## Recommended RBAC Model

Không share một `cluster-admin` credential cho tất cả hệ thống.

Nên tách:

```text
FKE
 │
 ├── fke-admin
 │     └── Human/jump admin
 │
 ├── argocd-manager
 │     └── Argo CD only
 │
 ├── prometheus
 │     └── Monitoring only
 │
 └── ci-deployer
       └── CI only
```

| Consumer | ServiceAccount | Permission |
|---|---|---|
| Admin jump host | `fke-admin` | cluster-admin hoặc custom |
| Argo CD | `argocd-manager` | Argo-specific |
| Monitoring | dedicated SA | read-only |
| CI/CD | dedicated SA | namespace-specific |
| Developer | Prefer short-lived human credential | RBAC theo user |

Không dùng một token admin cho Argo, CI, Jenkins, Prometheus và laptop cùng lúc.

---

## Security

Long-lived ServiceAccount token là static credential.

Nó giải quyết việc FPT client certificate hết hạn sau khoảng 24h, nhưng đổi lại token admin trở thành high-value credential.

Do đó:

1. Không commit kubeconfig vào Git.
2. Không gửi token qua chat/email.
3. File kubeconfig nên `chmod 600`.
4. Mỗi automation dùng một ServiceAccount riêng.
5. Giới hạn RBAC nếu không cần `cluster-admin`.
6. Rotate ngay nếu token bị lộ.
7. Human access lâu dài nên ưu tiên OIDC/SSO nếu FPT hỗ trợ.

Kubernetes khuyến nghị TokenRequest short-lived token cho phần lớn use case. Manual ServiceAccount token Secret vẫn được hỗ trợ khi cần credential không hết hạn, nhưng có security risk cao hơn.

---

## Troubleshooting

### Token Secret không có token

```bash
kubectl -n kube-system get secret fke-admin-token \
  -o jsonpath='{.data.token}'
```

Nếu empty, kiểm tra:

```bash
kubectl -n kube-system get secret fke-admin-token -o yaml
```

Phải có:

```yaml
type: kubernetes.io/service-account-token

metadata:
  annotations:
    kubernetes.io/service-account.name: fke-admin
```

Check ServiceAccount:

```bash
kubectl -n kube-system get sa fke-admin
```

### Unauthorized

```text
error: You must be logged in to the server (Unauthorized)
```

Check:

```bash
kubectl -n kube-system get secret fke-admin-token
kubectl -n kube-system get sa fke-admin
```

Kiểm tra token có dữ liệu:

```bash
kubectl -n kube-system get secret fke-admin-token \
  -o jsonpath='{.data.token}' |
base64 -d |
wc -c
```

### Forbidden

Ví dụ:

```text
nodes is forbidden:
User "system:serviceaccount:kube-system:fke-admin"
cannot list resource "nodes"
```

Authentication đã thành công. Lỗi nằm ở RBAC.

```bash
kubectl get clusterrolebinding \
  fke-admin-cluster-admin \
  -o yaml
```

Check permission:

```bash
kubectl auth can-i list nodes \
  --as=system:serviceaccount:kube-system:fke-admin
```

### TLS error

```text
x509: certificate signed by unknown authority
```

Check CA:

```bash
kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  view --raw \
  -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' |
base64 -d |
openssl x509 -noout -subject -issuer -dates
```

Không dùng `insecure-skip-tls-verify: true` để che lỗi CA.

---

## Quick Install

```bash
set -euo pipefail

SA_NAMESPACE="kube-system"
SA_NAME="fke-admin"
SA_SECRET="fke-admin-token"
OUTPUT_KUBECONFIG="$HOME/.kube/fke-admin.yaml"

echo "==> Verify current FPT kubeconfig"
kubectl get --raw=/version >/dev/null

SERVER=$(
  kubectl config view --raw --minify \
    -o jsonpath='{.clusters[0].cluster.server}'
)

echo "API Server: $SERVER"

echo "==> Create ServiceAccount"
kubectl -n "$SA_NAMESPACE" create serviceaccount "$SA_NAME" \
  --dry-run=client -o yaml |
kubectl apply -f -

echo "==> Create ClusterRoleBinding"
kubectl create clusterrolebinding fke-admin-cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount="${SA_NAMESPACE}:${SA_NAME}" \
  --dry-run=client -o yaml |
kubectl apply -f -

echo "==> Create long-lived token Secret"
cat <<EOF2 | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: ${SA_SECRET}
  namespace: ${SA_NAMESPACE}
  annotations:
    kubernetes.io/service-account.name: ${SA_NAME}
type: kubernetes.io/service-account-token
EOF2

echo "==> Wait for token"
for i in $(seq 1 30); do
  TOKEN_DATA=$(
    kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
      -o jsonpath='{.data.token}' 2>/dev/null || true
  )

  if [ -n "$TOKEN_DATA" ]; then
    break
  fi

  sleep 2
done

if [ -z "${TOKEN_DATA:-}" ]; then
  echo "ERROR: ServiceAccount token was not populated"
  exit 1
fi

TOKEN=$(printf '%s' "$TOKEN_DATA" | base64 -d)

echo "==> Extract CA"
kubectl -n "$SA_NAMESPACE" get secret "$SA_SECRET" \
  -o jsonpath='{.data.ca\.crt}' |
base64 -d > /tmp/fke-ca.crt

echo "==> Build kubeconfig"
mkdir -p "$(dirname "$OUTPUT_KUBECONFIG")"
rm -f "$OUTPUT_KUBECONFIG"

kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  set-cluster fpt-fke \
  --server="$SERVER" \
  --certificate-authority=/tmp/fke-ca.crt \
  --embed-certs=true

kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  set-credentials "$SA_NAME" \
  --token="$TOKEN"

kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  set-context fpt-fke-admin \
  --cluster=fpt-fke \
  --user="$SA_NAME"

kubectl config \
  --kubeconfig="$OUTPUT_KUBECONFIG" \
  use-context fpt-fke-admin

chmod 600 "$OUTPUT_KUBECONFIG"
rm -f /tmp/fke-ca.crt

unset TOKEN
unset TOKEN_DATA

echo "==> Verify"
KUBECONFIG="$OUTPUT_KUBECONFIG" kubectl get nodes

echo
echo "Created:"
echo "$OUTPUT_KUBECONFIG"
```

---

## Final State

Before:

```text
FPT Portal
   ↓
temporary kubeconfig
   ↓
X.509 client cert
   ↓
~24h
   ↓
EXPIRED
```

After:

```text
FPT temporary kubeconfig
        ↓
bootstrap once
        ↓
ServiceAccount: fke-admin
        ↓
manual ServiceAccount Token Secret
        ↓
fke-admin.yaml
        ↓
kubectl / Lens / jump host
```

Original FPT kubeconfig có thể hết hạn mà không ảnh hưởng đến ServiceAccount kubeconfig.

---

## References

- Kubernetes - Managing Service Accounts  
  https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/

- Kubernetes - Service Accounts  
  https://kubernetes.io/docs/concepts/security/service-accounts/

- Kubernetes - RBAC Authorization  
  https://kubernetes.io/docs/reference/access-authn-authz/rbac/

- Kubernetes - kubectl create token  
  https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_token/
