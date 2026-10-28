---
type: reference
provenance: source
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Thực tế tính đến 2026-10-28 (kiểm bằng kubectl chỉ đọc, context fsel-prod): số trong ảnh user gửi (2 node, 109.1 cores, 218.2 GiB) khớp với 2 node có label node_role=appnodes-prod2. Máy 64C128G thuộc pool prod3 nhưng vẫn mang label prod2. Có thêm 3 node node_role=appnodes-prod (Large-8) không nằm trong ảnh. Namespace fsel-prod có 42 deploy/sts và 30 HPA, mỗi HPA có 2 target (CPU và RAM), minReplicas 1 đến 5, maxReplicas phần lớn là 100; event-production đang 0 replica. Cluster có metrics-server và kube-state-metrics, chưa thấy Prometheus hay Grafana trong cluster. Nguồn: [[kubectl fsel-prod]] (2026-10-28).
