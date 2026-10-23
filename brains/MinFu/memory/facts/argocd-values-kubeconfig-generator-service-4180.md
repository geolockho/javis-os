---
type: reference
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Chart fsel đặt targetPort của Service bằng service.port. App kubeconfig-generator chỉ nghe 127.0.0.1:8000, nên giá trị cũ 8000 làm Ingress không vào được. Đã đổi service.port sang 4180, cổng của oauth2-proxy, và bản render cho Service lẫn Ingress đều trỏ 4180 (thực tế tính đến 2026-10-23, theo báo cáo của Javis). Thêm containerPort 8000 và securityContext không root, uid 10001, rootfs chỉ đọc, drop ALL cho khớp manifest gốc. [[conversations/2026-10-23]]
