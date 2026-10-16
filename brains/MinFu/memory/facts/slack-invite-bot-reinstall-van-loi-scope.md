---
superseded_by: slack-da-ket-noi-kenh-alert-fsel-prod
type: business
provenance: user
origin: javis-learned
created: 2026-10-13
updated: 2026-10-13
---
Ngày 2026-10-13, người dùng đã mời bot Javis vào kênh Slack của workspace Minh Phú Space bằng /invite @Javis. Người dùng cũng đã thêm bot scope chat:write, channels:read, channels:history, users:read trên api.slack.com và bấm Reinstall to Workspace. Sau đó bấm Reconnect trong Javis vẫn gặp lỗi "Invalid permissions requested / No scopes requested" (thực tế tính đến 2026-10-13). Nguyên nhân chưa xác minh (cần xác minh): trợ lý đoán link OAuth do Javis tạo có scope= (bot) để trống và chỉ có user_scope=, nên có thể cần thêm User Token Scopes. Chưa kiểm chứng.


## Lịch sử
- [2026-10-14] Bị thay thế bởi [[slack-da-ket-noi-kenh-alert-fsel-prod]] (user đổi thông tin).
