---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-09
updated: 2026-10-09
---
Người dùng yêu cầu viết trivy-scan.yml nhưng chưa gắn vào general.yml, và muốn scan xong mới push image (xem [[conversations/2026-10-09]]).

**Vì sao:** lý do chưa được người dùng nêu.
**Áp dụng:** khi có yêu cầu gắn Trivy vào pipeline, giữ thứ tự build, scan, rồi mới push; hỏi lại trước khi sửa general.yml.
