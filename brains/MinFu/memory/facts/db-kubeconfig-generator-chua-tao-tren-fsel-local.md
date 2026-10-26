---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
- Javis kiểm bằng lệnh chỉ đọc trong postgresql-0 (namespace postgresql-local-fsel, cluster fsel-local). Role kubeconfig_generator và DB kubeconfig_generator đều chưa tồn tại (thực tế tính đến 2026-10-26).
- Postgres trả password failed kể cả khi role không tồn tại, nên lỗi dễ bị hiểu nhầm là sai mật khẩu.
- Mật khẩu lấy từ DATABASE_URL trong secret kubeconfig-generator-env, do người dùng tự đặt.
**Áp dụng:** tạo role và DB trước khi restart pod.
