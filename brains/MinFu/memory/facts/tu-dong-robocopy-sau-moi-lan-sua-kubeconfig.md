---
type: preference
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Người dùng yêu cầu sau mỗi lần sửa code kubeconfig-generator trong workspace thì Javis tự robocopy sang D:\FSEL\other-services\kubeconfig-generator, không cần hỏi lại (ngày 2026-10-23, [[conversations/2026-10-23]]). Lệnh robocopy đã chốt trước đó loại trừ .git, .venv, __pycache__ và .env (ghi nhận từ [[viet-code-kubeconfig-generator-trong-brain-roi-copy]]). **Áp dụng:** sau mỗi lần sửa file trong workspace/kubeconfig-generator, chạy robocopy với các loại trừ trên và báo ngắn đã sync. Lý do người dùng muốn tự động chưa được nêu.
