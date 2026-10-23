---
superseded_by: code-kubeconfig-generator-da-co-trong-workspace
type: business
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
source: chat 2026-10-23 (cf8a38f9)
---
Thực tế tính đến 2026-10-23:
- Kiến trúc đã duyệt, DB chỉ dùng PostgreSQL.
- Domain là `kubeconfig-generator.fsel.edu.vn`, Redirect URI là `/oauth2/callback`.
- Người dùng đã nói "oke viết đi": viết code trong brain tại `workspace/kubeconfig-generator` rồi copy sang repo.
- Người dùng không biết cách decode ID token để xem claim groups. Javis sẽ làm endpoint `/admin/debug/claims` chỉ admin gọi được, và tên claim đọc từ biến `GROUP_CLAIM` (mục tiêu).
- Người dùng sẽ tự khai báo Argo CD sau, và sẽ cung cấp namespace test sau khi deploy.
- Chưa xác nhận phiên bản GitLab và tên claim `groups` thật.


## Lịch sử
- [2026-10-23] Bị thay thế bởi [[code-kubeconfig-generator-da-co-trong-workspace]] (user đổi thông tin).
