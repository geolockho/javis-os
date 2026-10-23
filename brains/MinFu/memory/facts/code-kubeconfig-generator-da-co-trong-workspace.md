---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Thực tế tính đến 2026-10-23 (đã xác nhận bằng liệt kê file trong brain):
- Code nằm tại `workspace/kubeconfig-generator`, gồm `app/`, `tests/` và `scripts/gen_rbac.py`.
- Báo cáo của Javis trong chat: chạy 69 test qua, 1 test bỏ qua (test trên cluster thật, chờ namespace test). Chưa chạy lại để kiểm chứng.
- Chưa commit, chưa push. Cổng soát RBAC lần 2 chưa chạy (theo báo cáo của Javis).
- Bản copy sang `D:\FSEL\other-services\kubeconfig-generator` qua robocopy: chưa kiểm chứng.
- Các TODO trong `deploy/` (registry image, ingressClassName, nhãn namespace ingress, địa chỉ Postgres trong NetworkPolicy) chưa xong.
