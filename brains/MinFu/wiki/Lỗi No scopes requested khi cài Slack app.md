---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-10-13
updated: 2026-10-13
source: [[conversations/2026-10-13]]
---
Slack báo "Invalid permissions requested / No scopes requested" khi cài app, khi link OAuth có scope= (quyền bot) rỗng và chỉ có user_scope= (thực tế tính đến 2026-10-13) [[conversations/2026-10-13]]. Nguyên nhân cụ thể trong trường hợp này là link do Javis tạo ra (cần xác minh) [[conversations/2026-10-13]]. Cách kiểm tra là đọc tham số scope= trong link trước khi bấm đăng nhập (cần xác minh) [[conversations/2026-10-13]].
