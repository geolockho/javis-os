---
superseded_by: lich-jira-hang-ngay-5h30-hai-tai-khoan
type: decision
provenance: user
origin: javis-learned
created: 2026-11-02
updated: 2026-11-02
---
Mục tiêu đã chốt: chạy lúc 18:00 từ thứ 2 đến thứ 6 cho hai tài khoản Jira. Mỗi lượt tạo Task trong dự án FD theo mẫu tương ứng, chuyển từ To Do sang In Progress, log work 6 giờ rồi chuyển sang Done. Nếu tạo issue thất bại thì bỏ qua log work, không tạo bù. Bỏ qua trường Team production. Gửi thông báo vào Slack channel C0CDCRXNR2A. Mỗi lịch cần dùng đúng MCP/tài khoản Jira tương ứng: hophu qua Jira Fsel, nguyenviet qua Jira hoangviet.

## Kết quả lần chạy đầu ngày 2026-11-02
- Cả FD-5 (việc hophu) và FD-6 (việc nguyenviet) được tạo dưới tài khoản `nguyenviet`, do MCP Jira Fsel khi đó đang dùng nhầm PAT của nguyenviet. Không rõ ai hoặc thao tác nào đã đổi PAT.
- FD-5 được chuyển Done và có worklog 6 giờ do Nguyễn Hoàng Việt ghi, sai người so với lịch hophu. FD-6 ban đầu thiếu label DevOps và due date; label DevOps đã được thêm sau đó, rồi FD-6 được xác nhận Done. Lần kiểm tra cuối không trả trường due date nên trạng thái due date vẫn chưa xác minh.
- Người dùng nhập lại PAT hophu. Kiểm tra chỉ đọc ngày 2026-11-02 bằng JQL `reporter = currentUser()` xác nhận Jira Fsel trả issue của `hophu`, còn Jira hoangviet trả issue của `nguyenviet`.
- Hai lịch đã được sửa để kiểm tra danh tính trước khi tạo issue và dừng/báo Slack nếu tài khoản không khớp. Lịch nguyenviet kiểm tra và tự bổ sung label DevOps hoặc due date bằng ngày tạo nếu còn thiếu.
- Tính đến hội thoại ngày 2026-11-02, FD-5 vẫn có worklog sai người; chưa có yêu cầu xử lý dữ liệu cũ. Due date FD-6 chưa xác minh.


## Lịch sử
- [2026-11-03] Bị thay thế bởi [[lich-jira-hang-ngay-5h30-hai-tai-khoan]] (user đổi thông tin).
