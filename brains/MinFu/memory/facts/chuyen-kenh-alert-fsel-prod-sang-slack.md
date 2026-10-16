---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-13
updated: 2026-10-13
---
**Quyết định:** kênh nhận thống kê và alert CPU/RAM của context fsel-prod, ns fsel-prod chuyển từ Zalo sang Slack.

**Vì sao:** nguồn Zalo (Minh Phú) đang không kết nối được tại thời điểm 2026-10-13, nên workflow gửi Zalo sẽ thất bại mà không ai biết.

**Áp dụng:** khi dựng workflow, đấu một Slack MCP vào Javis rồi gửi qua Slack. Cần Channel ID của kênh nhận và ngưỡng alert, người dùng chưa cung cấp.
