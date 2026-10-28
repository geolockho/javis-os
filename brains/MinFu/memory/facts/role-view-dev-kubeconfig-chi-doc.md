---
type: reference
provenance: source
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Javis đọc ClusterRole `view` trên fsel-local ngày 2026-10-28 và tóm tắt cho user ([[conversations/2026-10-28]]).

- **Xem được**: workload (pod, deployment, statefulset, job...), service, ingress, networkpolicy, **configmap**, serviceaccount, PVC, events, `pods/log`, và `kubectl top` cho pod. Có thêm CRD cert-manager và Kyverno.
- **Không xem được**: Secret, và mọi thao tác ghi (create, patch, delete, exec, port-forward, scale). Node và namespace cấp cluster không xem được.
- **Rủi ro**: ConfigMap và pods/log có thể lộ mật khẩu hoặc token nếu team để trong đó.
- Role của tool `kubeconfig-generator-issuer` khác role của dev, Kyverno bind vào từng namespace có label ([[kyverno-dang-chay-tren-hai-cluster]]).

Chưa kiểm fsel-prod, nếu bản Kubernetes hoặc Kyverno khác thì danh sách có thể khác (cần xác minh). Chưa chạy `kubectl auth can-i --list` với kubeconfig dev thật.
