---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
Trước khi commit, Javis quét file đã stage tìm cert, private key, JWT, token dài và Slack webhook, không thấy gì. Bản trên GitLab chỉ có deploy/secret.example.yaml (theo báo cáo của Javis, chưa xác minh trên GitLab).
**Vì sao:** secret.yaml từng chứa cert admin fsel-local và token fsel-prod.
**Áp dụng:** trước mỗi lần push repo này, kiểm git check-ignore cho deploy/secret.yaml và secrets/.
