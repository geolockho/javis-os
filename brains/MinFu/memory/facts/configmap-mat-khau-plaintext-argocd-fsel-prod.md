---
type: business
provenance: source
origin: javis-learned
created: 2026-10-29
updated: 2026-10-29
---
Ngày 2026-10-28, khi tìm chỗ khai báo HPA, Javis đã đọc nhầm một file trong `D:\argocd-deploy-clean\values\fsel-prod\templates` và thấy ConfigMap chứa mật khẩu DB và secret key dạng plaintext. Chưa kiểm lại trạng thái hiện tại (cần xác minh).

**Vì sao:** Thông tin nhạy cảm nằm trong repo dạng plaintext là rủi ro bảo mật, nên cần chuyển sang Secret.
**Áp dụng:** Khi làm báo cáo tài nguyên fsel-prod, chỉ đọc `values.yaml`, không đọc `templates/`.
