---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Người dùng chốt cách B cho kubeconfig-generator: namespace có label kubeconfig-generator/enabled=true thì Kyverno policy generate sinh RoleBinding cho SA của tool, policy validate chỉ cho group admin thêm, sửa, xoá label kubeconfig-generator/*, và exclude cứng kube-system, kyverno, cd, haproxy, rabbitmq, redis (ngày 2026-10-23, [[conversations/2026-10-23]]). Admin gán label bằng tay: kubectl label ns <namespace> kubeconfig-generator/enabled=true. Đây là quyết định hướng đi, mục tiêu chưa làm; hiện trạng code vẫn là whitelist configmap-namespaces.yaml (thực tế tính đến 2026-10-23). Phiên bản Kyverno hợp với fsel-prod 1.25 và fsel-local 1.34 chưa đối chiếu ma trận tương thích (cần xác minh) [[conversations/2026-10-23]]. **Vì sao:** Javis đã nêu rủi ro của các cách khác: cách C không chạy được trên 1.25 vì chưa có ValidatingAdmissionPolicy, cách D là leo thang quyền; người dùng chọn B sau khi biết cách B vẫn không chặn được cluster-admin [[conversations/2026-10-23]]. **Áp dụng:** app đọc danh sách namespace theo label thay ConfigMap, thêm deploy/kyverno/, bỏ sinh RoleBinding theo namespace khỏi gen_rbac.py, cập nhật README và test; thay đổi trong workspace phải robocopy sang repo D:\FSEL\other-services\kubeconfig-generator.
