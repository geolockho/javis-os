---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
- Thực tế tính đến 2026-10-14: thẻ Slack (workspace Minh Phú Space) đã kết nối thành công, trạng thái ổn, quyền đang là full. Các lỗi trước đó (401 missing_token, No scopes requested) không còn là vấn đề hiện hành. [[conversations/2026-10-14]]
- Kênh nhận thống kê và alert CPU/RAM của fsel-prod: `C0C8RMMB7AN`. Link: https://minhphspace.slack.com/archives/C0C8RMMB7AN. Bot Javis đã được mời vào kênh. [[conversations/2026-10-14]]
- Tin nhắn thử đã gửi thành công vào kênh này, nên bot có quyền post. [[conversations/2026-10-14]]
- Người dùng muốn chỉ dùng Slack cho alert này. Zalo giữ để dùng cho việc khác, không tắt. [[conversations/2026-10-14]]
- Slack và Zalo đang cùng được đánh dấu mặc định. Nếu không bỏ cờ mặc định ở thẻ Zalo thì phải chỉ định rõ Slack mỗi lần gửi. [[conversations/2026-10-14]]

**Vì sao:** Zalo từng hỏng và người dùng muốn tách kênh. **Áp dụng:** mọi báo cáo và alert fsel-prod gửi vào `C0C8RMMB7AN` qua Slack, không gửi Zalo.
