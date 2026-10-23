---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Thực tế tính đến 2026-10-23: bản code trong brain có 69 test qua và 1 test bỏ qua (test cần cluster thật). Đã thêm `.gitlab-ci.yml` vào gốc repo theo file user gửi, và đổi namespace của tool sang fsel-internal-tools ([[ns-kubeconfig-generator-fsel-internal-tools]]). Chưa commit, chưa push, và chưa chạy cổng soát RBAC lần 2 theo workflow đã chốt. Còn mở: quyết định có bỏ object Namespace khỏi manifest RBAC hay không, và các TODO trong deploy/ gồm registry image, ingressClassName, nhãn namespace của ingress controller, địa chỉ Postgres trong NetworkPolicy. Đây là hiện trạng, không phải mục tiêu. Tiếp nối [[tien-do-kubeconfig-generator-2026-10-23]] và [[viet-code-kubeconfig-generator-trong-brain-roi-copy]].
