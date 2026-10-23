---
type: business
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Theo lời user ngày 2026-10-23, FKE không giới hạn hạn token TokenRequest, nên kubeconfig cấp cho dev có thể đặt hạn một tháng. [[conversations/2026-10-23]]
Trạng thái: thực tế theo lời user, chưa đo bằng lệnh trên cluster (cần xác minh). Wiki Kubeconfig ServiceAccount cho FPT FKE ghi TTL chưa xác minh, chưa khẳng định giới hạn nào.
**Áp dụng:** Khi viết công cụ cấp kubeconfig, không cần xử lý trường hợp hạn bị cắt ngắn. Kiểm chứng hạn thật khi chạy kiểm thử.
