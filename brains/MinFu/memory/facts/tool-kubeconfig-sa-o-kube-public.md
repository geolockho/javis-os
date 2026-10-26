---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
Người dùng đã đổi deploy/rbac/tool.yaml, policy Kyverno và script sang kube-public, rồi báo Javis kiểm tra (thực tế tính đến 2026-10-26, [[conversations/2026-10-26]]). Namespace fsel-internal-tools vẫn nằm trong danh sách cấm vì Secret chứa token của tool ở đó. Áp dụng: khi sửa RBAC hoặc policy của kubeconfig-generator, lấy kube-public làm namespace của SA.
