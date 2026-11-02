---
type: decision
provenance: user
origin: javis-learned
created: 2026-11-02
updated: 2026-11-02
---
Người dùng chốt hai lịch Jira chạy lúc 18:00 từ thứ Hai đến thứ Sáu, bắt đầu từ tuần sau ngày 2026-11-02. Mỗi lịch tạo một Task trong dự án FD, Due date là ngày tạo, Priority Medium; bỏ qua trường Team production nếu không đặt được. Issue chuyển từ To Do sang In Progress, log work 6h với ngày bắt đầu mặc định và Remaining Estimate tự điều chỉnh, rồi chuyển sang Done. Nếu tạo issue thất bại thì bỏ qua log work, không tạo bù. Báo kết quả vào Slack channel C0CDCRXNR2A. Mẫu hophu: summary "Theo dõi, giám sát hệ thống", assignee Hồ Minh Phú, label DevOps, description gồm theo dõi hệ thống, tối ưu tài nguyên và xử lý sự cố nếu có. Mẫu hoangviet: summary "Lịch kiểm tra", assignee Nguyễn Hoàng Việt, description gồm kiểm tra backup database, alert Teams, xử lý sự cố và đề xuất giải pháp khắc phục. Người dùng đồng ý dùng tài khoản Jira hoangviet cho lịch tự động.
