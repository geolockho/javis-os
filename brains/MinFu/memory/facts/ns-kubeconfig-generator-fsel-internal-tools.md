---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Ngày 2026-10-23 user yêu cầu đổi hết namespace của công cụ kubeconfig-generator sang `fsel-internal-tools` ([[conversations/2026-10-23]]). Tên tài nguyên như Deployment, ServiceAccount, Secret và ClusterRole vẫn giữ `kubeconfig-generator`. Namespace của dev trong group map chỉ là ví dụ nên không đổi. Việc user có muốn bỏ object Namespace khỏi manifest RBAC hay không vẫn đang chờ quyết định (thực tế tính đến 2026-10-23).
