---
type: reference
provenance: user
origin: javis-learned
created: 2026-10-29
updated: 2026-10-29
---
Ngày 2026-10-29 user yêu cầu thêm link tải Lens để dev dùng ở trang download của kubeconfig-generator [[conversations/2026-10-29]]. Link: https://api.k8slens.dev/binaries/Lens%20Setup%202026.10.261408-latest.exe

- Javis đã thêm thẻ Lens (Windows) trong app/templates/download.html, ghi rõ là không bắt buộc, dev dùng kubectl vẫn được. Nút mở tab mới với rel="noopener noreferrer" (thực tế tính đến 2026-10-29).
- Đã sync sang repo FSEL nhưng chưa commit, chưa push và chưa render trang (thực tế tính đến 2026-10-29).
- Link trả 302 khi kiểm bằng curl -I. Chưa tải bộ cài về nên chưa xác minh được file (cần xác minh).
- Tên file có số phiên bản cố định, nên nút hỏng nếu Lens đổi tên hoặc gỡ bản này.
- Trang /dl chặn theo IP qua whitelist-source-range, dev ngoài dải IP không thấy nút.
