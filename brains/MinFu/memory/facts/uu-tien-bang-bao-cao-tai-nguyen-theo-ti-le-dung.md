---
type: preference
provenance: user
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Ngày 2026-10-28 người dùng yêu cầu bảng thống kê tài nguyên fsel-prod (tin 2 tiếng và tổng kết cuối ngày) có chữ to hơn một cỡ và sắp xếp tăng dần theo tỉ lệ usage/request, để thấy service nào đang request nhiều mà ít dùng. [[conversations/2026-10-28]]

Tiêu chí xếp cụ thể (trung bình %CPU và %RAM dùng/request) là phương án Javis đề xuất, người dùng chưa chọn: đang chờ người dùng xác nhận giữa giữ nguyên, theo %CPU, hoặc theo lượng thừa (cần xác minh).

**Vì sao:** người dùng cần tìm service request dư để giảm lãng phí tài nguyên. **Áp dụng:** khi dựng bảng báo cáo, giữ thứ tự tăng dần theo tỉ lệ dùng/request; nếu người dùng chọn tiêu chí khác thì đổi theo lựa chọn đó.
