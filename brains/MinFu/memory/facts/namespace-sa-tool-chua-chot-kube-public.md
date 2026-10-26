---
superseded_by: tool-kubeconfig-sa-o-kube-public
type: decision
provenance: javis-learned
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
Ngày 2026-10-26 user tự sửa `deploy/rbac/tool.yaml` trong repo D:\FSEL\other-services\kubeconfig-generator, đổi namespace của ServiceAccount và RBAC của tool sang `kube-public`, trong khi Deployment vẫn ở `fsel-internal-tools` ([[conversations/2026-10-26]]). Javis trả lời khác namespace vẫn chạy được, vì app dùng token trong kubeconfig lấy từ Secret chứ không dùng SA của pod. Chưa chốt, Javis đang chờ user chọn một trong ba hướng:

1. Giữ `kube-public`, sửa policy Kyverno và thêm gitignore.
2. Đổi sang namespace riêng `kubeconfig-generator`. Tên có chữ `kube` nên app và Kyverno tự loại, không cần thêm vào danh sách cấm.
3. Chỉ thêm `deploy/secret.yaml` vào gitignore.

**Vì sao:** `kube-public` là namespace công khai theo quy ước. Nếu sau này ai cấp quyền đọc rộng ở đó, token dài hạn của tool sẽ lộ. Kyverno cũng nên nằm trong namespace riêng, không chung với tool.

**Áp dụng:** trước khi commit, hỏi lại user chọn hướng nào. Brain và repo đang lệch nhau: repo đã đổi sang `kube-public`, brain vẫn ghi `fsel-internal-tools`. Liên quan [[ns-kubeconfig-generator-fsel-internal-tools]] và [[secret-yaml-admin-chua-gitignore]].


## Lịch sử
- [2026-10-26] Bị thay thế bởi [[tool-kubeconfig-sa-o-kube-public]] (user đổi thông tin).
