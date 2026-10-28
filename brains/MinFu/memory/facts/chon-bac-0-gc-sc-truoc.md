---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Ngày 2026-10-28 user chọn bắt đầu đoạn gc → sc ở bậc 0 (HTTP thường, chỉ whitelist IP) [[conversations/2026-10-28]]. Bậc 1 (TLS một chiều) và bậc 2 (mTLS) được viết sẵn để nâng cấp sau, chưa triển khai [[conversations/2026-10-28]].

**Vì sao:** user muốn đi từ đơn giản trước, nâng bậc sau bằng cách đổi annotation thay vì đổi kiến trúc [[conversations/2026-10-28]].

**Áp dụng:** khi user hỏi về gc → sc, mặc định trả lời theo bậc 0. Lên bậc 1 khi có cert nội bộ, lên bậc 2 trước khi cutover prod đi qua Internet (mục tiêu) [[conversations/2026-10-28]].
