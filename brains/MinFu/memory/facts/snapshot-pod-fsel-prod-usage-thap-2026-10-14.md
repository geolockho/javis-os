---
type: reference
provenance: source
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
Mẫu tức thời lấy bằng kubectl top lúc 13:55 ngày 2026-10-14 trong context fsel-prod, không phải trung bình theo thời gian [[conversations/2026-10-14]]. Có 6 pod dưới 10% cả CPU lẫn RAM: aggregation-worker-prod (3 pod, CPU 2m/50m, RAM 23-27Mi/300Mi) và tracking-worker-prod (3 pod, CPU 1-2m/300m, RAM 17-24Mi/300Mi) [[conversations/2026-10-14]]. Trong 85 pod có số liệu, 69 pod có CPU dưới 10% request [[conversations/2026-10-14]]. Hai pod chưa có số liệu usage: fsel-exam-production-f6c9bb97c-bhtr2 và fsel-portal-landing-web-backup-6b5cbfd7ff-c9x4m [[conversations/2026-10-14]]. Mức dùng lúc cao điểm chưa được kiểm tra (cần xác minh).
