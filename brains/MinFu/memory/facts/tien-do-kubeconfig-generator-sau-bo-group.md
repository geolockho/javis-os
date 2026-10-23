---
type: reference
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Đến 2026-10-23: 77 test qua, 1 test bỏ qua (cần cluster thật). Đã đổi sang danh sách namespace: ConfigMap kubeconfig-generator-namespaces, biến NAMESPACES_PATH, gen_rbac.py đọc thẳng ConfigMap, thư mục config/ đã xoá. Code đã đồng bộ sang repo nhưng chưa commit, chưa push.

Còn mở:
- Chạy cổng soát RBAC lần 2 trước khi push.
- Chốt domain email cho oauth2-proxy.
- Chốt có bỏ object Namespace khỏi RBAC không, vì ArgoCD prune có thể xoá namespace dùng chung.
- Secret đã tạo với GROUP_MAP_PATH thì tạo lại với NAMESPACES_PATH.
