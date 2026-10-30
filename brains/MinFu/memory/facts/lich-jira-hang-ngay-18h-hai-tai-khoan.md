---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-30
updated: 2026-10-30
---
Người dùng chốt chạy từ thứ Hai đến thứ Sáu lúc 18:00, bắt đầu từ tuần sau (2026-11-02). Với mỗi tài khoản, tạo một issue loại Task theo mẫu, chuyển To Do sang In Progress, log work 6h với ngày bắt đầu mặc định và remaining estimate tự điều chỉnh, rồi chuyển sang Done. Nếu tạo issue thất bại thì bỏ qua log work, không tạo bù. Bỏ qua trường Team production. Gửi thông báo vào Slack channel `C0CDCRXNR2A`.

- **hophu:** summary “Theo dõi, giám sát hệ thống”; description gồm theo dõi hệ thống, tối ưu tài nguyên, xử lý sự cố nếu có; assignee Hồ Minh Phú.
- **hoangviet:** summary “Lịch kiểm tra”; description gồm kiểm tra backup database, alert Teams, xử lý và khắc phục sự cố; assignee Nguyễn Hoàng Việt.
- Cả hai: viết hoa chữ đầu summary, priority Medium, label DevOps. Người dùng đồng ý cho quy trình dùng MCP Jira hoangviet.
