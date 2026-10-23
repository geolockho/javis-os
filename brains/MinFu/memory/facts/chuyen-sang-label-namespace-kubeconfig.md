---
superseded_by: chot-cach-b-kyverno-label-namespace
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Người dùng chọn hướng dùng label namespace thay cho whitelist `configmap-namespaces.yaml` (ngày 2026-10-23, [[conversations/2026-10-23]]). Đây là lựa chọn hướng đi, chưa phải đã triển khai (mục tiêu, chưa làm).

**Vì sao:** Javis đề xuất để bỏ bước sửa ConfigMap và chạy lại `gen_rbac.py` mỗi khi thêm namespace. Lý do do Javis nêu, người dùng chưa nói thêm.

**Áp dụng:** Giai đoạn 1 (mục tiêu): namespace có label `kubeconfig-generator/enabled=true` là nguồn sự thật cho app, RBAC vẫn sinh từ Git. Giai đoạn 2 chỉ làm khi cài Kyverno (cluster fsel-prod hiện chưa có). Danh sách namespace hệ thống bị chặn vẫn nằm trong code. Phần còn đúng từ quyết định cũ: namespace phải tồn tại sẵn trên cả hai cluster, RBAC không sinh manifest Namespace [[conversations/2026-10-23]].


## Lịch sử
- [2026-10-23] Bị thay thế bởi [[chot-cach-b-kyverno-label-namespace]] (user đổi thông tin).
