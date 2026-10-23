---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
**Quyết định:** user yêu cầu bỏ manifest tạo namespace khỏi `deploy/rbac`. `scripts/gen_rbac.py` không sinh object `Namespace` nữa. `fsel-internal-tools` và mọi namespace dev phải được tạo sẵn trên cả fsel-prod và fsel-local, nếu thiếu thì `apply` báo `namespace not found` (thực tế tính đến 2026-10-23) [[conversations/2026-10-23]].

**Giữ whitelist:** `deploy/configmap-namespaces.yaml` vẫn là nguồn duy nhất, namespace phải khai báo trước khi dev xin quyền. User chọn giữ whitelist thay vì dùng label `kubeconfig-generator/enabled=true`. Hướng label chỉ là đề xuất, chưa triển khai (mục tiêu, chưa chốt) [[conversations/2026-10-23]].

**Áp dụng:** khi thêm namespace mới, sửa ConfigMap rồi chạy `gen_rbac.py --catalog deploy/configmap-namespaces.yaml --out deploy/rbac`. Không đưa lại object Namespace vào RBAC. Liên quan [[ns-kubeconfig-generator-fsel-internal-tools]] và [[bo-group-gitlab-dung-danh-sach-namespace]].
