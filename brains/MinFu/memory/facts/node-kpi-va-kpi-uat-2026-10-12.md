---
type: business
provenance: user
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
Theo kết quả `kubectl get nodes` người dùng tự chạy và dán ngày 2026-10-12 (thực tế tính đến 2026-10-12):

- **kpi**: 9 node, tất cả Ready, v1.36.2, tuổi 31 ngày. Gồm 3 control-plane (kpi-master-01/02/03) và 6 node còn lại: kpi-monitor, kpi-rabbitmq, kpi-redis, kpi-worker-01/02/03.
- **kpi-uat**: 3 node, tất cả Ready, v1.36.2, tuổi 12 ngày. Gồm 1 control-plane (uat-cntt-kpi-master-101) và 2 app node (uat-cntt-kpi-appnode1-99, uat-cntt-kpi-appnode2-98).

Javis chưa đọc trực tiếp từ cụm, đây là số liệu do người dùng dán.
