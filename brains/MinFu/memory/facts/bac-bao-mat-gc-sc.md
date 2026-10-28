---
superseded_by: chon-bac-0-gc-sc-truoc
type: decision
provenance: source
origin: javis-learned
created: 2026-10-27
updated: 2026-10-27
---
Đề xuất (chưa chốt) của Javis cho đoạn gc → sc là thang 3 bậc, đi từ thấp lên (ghi nhận 2026-10-27). [[conversations/2026-10-27]]

- Bậc 0: HTTP thường, chỉ whitelist IP. Dùng cho PoC đầu hoặc khi kênh riêng/VPN đã mã hoá.
- Bậc 1: TLS một chiều, gc xác thực cert sc bằng `ca.crt`. Dùng khi đi Internet nhưng chưa muốn quản client cert.
- Bậc 2: mTLS đầy đủ, hai bên xác thực nhau. Dùng cho prod nếu đường liên cloud đi Internet.
- Whitelist IP là lớp nền dùng chung cho mọi bậc.

**Vì sao:** đây là cách để một cấu hình đổi bậc chỉ cần sửa annotation, không đổi kiến trúc.

**Áp dụng:** nếu chưa có cert nội bộ thì bắt đầu ở bậc 0. Trước khi cutover prod qua Internet phải lên bậc 2. User chưa xác nhận lựa chọn bậc nào.

Liên quan: [[manifest-poc-gc-sc-gateway]], [[ke-hoach-tach-gateway-va-service-nhieu-cluster]].


## Lịch sử
- [2026-10-28] Bị thay thế bởi [[chon-bac-0-gc-sc-truoc]] (user đổi thông tin).
