---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
source: [[conversations/2026-10-26]]
---
oauth2-proxy từ chối `cookie_secret` không đúng độ dài và in thông báo `cookie_secret must be 16, 24, or 32 bytes ... but is N bytes` [[conversations/2026-10-26]]. Đã gặp N = 44 (base64 chuẩn 32 byte) và N = 64 (chuỗi hex 64 ký tự) (thực tế tính đến 2026-10-26) [[conversations/2026-10-26]]. Cách kiểm an toàn là đo độ dài chuỗi, không in giá trị secret ra chat [[conversations/2026-10-26]]. Giả thuyết cần xác minh: oauth2-proxy chỉ giải mã base64url nên base64 chuẩn có ký tự `+` hoặc `/` bị đếm thành byte thô (cần xác minh, chưa đối chiếu tài liệu chính thức) [[conversations/2026-10-26]].
