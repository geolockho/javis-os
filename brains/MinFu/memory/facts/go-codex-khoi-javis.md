---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-09
updated: 2026-10-09
---
Ngày 2026-10-09, người dùng đã disconnect Codex nhưng vẫn thấy Codex tiêu token. Người dùng yêu cầu quét các model đang hoạt động và xoá Codex khỏi tất cả hoạt động của Javis. Trong hội thoại, loop "Tổng hợp kiến thức" đã được xác nhận là tắt. Hai plugin dùng ChatGPT OAuth (Tạo và xem ảnh, Đọc ảnh trong nhóm Zalo) vẫn còn bật tại thời điểm đó; người dùng chưa quyết việc tắt hẳn hay giữ. Nguyên nhân tiêu token chưa xác minh (cần xác minh).

**Vì sao:** người dùng muốn kiểm soát hạn mức và không để Codex chạy ngầm sau khi đã ngắt kết nối.

**Áp dụng:** khi nói về Codex, ưu tiên gỡ hoàn toàn khỏi engine mặc định, agent, plugin; không đề xuất đưa Codex trở lại nếu người dùng chưa đổi ý.
