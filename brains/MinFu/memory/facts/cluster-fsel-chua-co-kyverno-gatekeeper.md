---
superseded_by: kyverno-dang-chay-tren-hai-cluster
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Ngày 2026-10-23 Javis kiểm trực tiếp hai cluster: **fsel-prod chạy Kubernetes v1.25.10**, **fsel-local chạy v1.34.0**, và cả hai đều chưa có Kyverno hay Gatekeeper (thực tế tính đến 2026-10-23, [[conversations/2026-10-23]]). Hệ quả: cách B (Kyverno generate RoleBinding theo label) cần cài Kyverno trước, và phải chọn bản hỗ trợ đúng từng phiên bản K8s. Bản Kyverno cụ thể cho từng cluster chưa xác minh (cần xác minh).


## Lịch sử
- [2026-10-26] Bị thay thế bởi [[kyverno-dang-chay-tren-hai-cluster]] (user đổi thông tin).
