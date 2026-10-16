---
type: reference
provenance: user
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
Người dùng dán output terminal kiểm tra cronjob backup etcd trên cụm kpi. Job etcd-snapshot-29863020 (lịch 12:00) có FAILED=1, SUCCEEDED trống, log container snapshot rỗng, Events không còn. Nguyên nhân chưa xác định; cần log --previous hoặc describe pod để khoanh lỗi. Liên quan: [[conversations/2026-10-12]]. Trạng thái này là ảnh chụp tại thời điểm đó, không phải hiện trạng hiện tại (cần xác minh lại).
