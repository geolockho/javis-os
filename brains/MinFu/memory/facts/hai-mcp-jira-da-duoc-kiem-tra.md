---
type: reference
provenance: assistant
origin: javis-learned
created: 2026-11-02
updated: 2026-11-02
---
Ngày 2026-11-02, người dùng báo đã thay PAT của hophu sau khi kết nối Jira của tài khoản này từng dùng nhầm token nguyenviet. Javis kiểm tra chỉ đọc bằng JQL `reporter = currentUser()`: Jira Fsel trả về issue của hophu, còn Jira hoangviet trả về issue của nguyenviet. Kết quả xác nhận trạng thái sau lần sửa tại thời điểm kiểm tra.
