---
type: preference
provenance: user
origin: javis-learned
created: 2026-10-08
updated: 2026-10-08
---
Người dùng muốn Javis tự động đánh giá độ lớn context và cắt hoặc xoay mạch khi một phiên dùng quá nhiều input token, nhằm tối ưu mức tiêu thụ thay vì chờ người dùng tự tách phiên.

**Vì sao:** Ngày 2026-10-08, dashboard cảnh báo một phiên nạp 1,1 triệu, sau đó 3,8 triệu input token. Người dùng hỏi vì sao đã tối ưu mà vẫn bị và yêu cầu kiểm tra, sửa lại.

**Áp dụng:** Bản đầu: cộng dồn input token trong mạch, xoay khi một lượt hoặc tổng tích lũy vượt 500.000, mạch mới mang tóm tắt và tối đa 300.000 ký tự lịch sử, cần ít nhất 4 message mới mới được xoay lại, đặt lại bộ đếm sau khi xoay. Trong lượt sau, Javis báo cảnh báo 3,8 triệu là tổng token cache của nhiều lần gọi trong một file Codex chứ không phải context của một lượt. Javis đang đổi cảnh báo sang đo đỉnh context của từng lần gọi và hạ ngưỡng xoay xuống 150.000 để kịp trước cửa sổ khoảng 258.000 của Codex. Phần này Javis tự nói, việc xác minh trên log bị ngắt giữa chừng (cần xác minh). Cần khởi động lại Javis để nạp mã mới.
