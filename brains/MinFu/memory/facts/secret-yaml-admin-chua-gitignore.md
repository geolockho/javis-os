---
superseded_by: secret-yaml-da-vao-gitignore
type: business
provenance: javis-learned
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
Ngày 2026-10-26 Javis đọc `deploy/secret.yaml` trong repo kubeconfig-generator và thấy hai vấn đề (thực tế tính đến 2026-10-26, [[conversations/2026-10-26]]):

- File chứa kubeconfig của **admin**, không phải token của SA `kubeconfig-generator`. Cert của fsel-local là `CN=kubernetes-admin` thuộc nhóm cluster-admins. Token của fsel-prod không phải JWT, có thể là token user của FKE, chưa xác định quyền. Nếu dùng các thông tin này, RBAC và Kyverno gần như không có tác dụng.
- File **không nằm trong `.gitignore`**. Javis đã kiểm bằng `git check-ignore` và thấy rằng commit lúc này sẽ đưa cert admin của fsel-local lên GitLab. Trước khi commit cần thêm dòng `deploy/secret.yaml` vào `.gitignore`.

**Cần làm:** thay cả hai bằng token lấy từ Secret `kube-public/kubeconfig-generator-token` trên từng cluster. Đây là đề xuất của Javis, chưa có user xác nhận; lần kiểm tra này chỉ đọc file, không sửa gì.

Liên quan [[namespace-sa-tool-chua-chot-kube-public]] và [[robocopy-thieu-xo-ghi-de-gitignore]].


## Lịch sử
- [2026-10-26] Bị thay thế bởi [[secret-yaml-da-vao-gitignore]] (user đổi thông tin).
