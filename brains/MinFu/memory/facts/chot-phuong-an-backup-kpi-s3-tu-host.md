---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-09
updated: 2026-10-09
---
Ngày 2026-10-09, người dùng chốt phương án backup cho cụm kpi (chưa có backup nào trước đó) và chọn đẩy bản backup ra S3 tự host.

- Người dùng tự điền endpoint, access key, secret key và bucket vào secret `backup-s3`; Javis chỉ để placeholder.
- Javis đã viết 3 manifest trong `infra/kpi-backup/` (secret, CronJob etcd, CronJob pg_dump) và chạy dry-run server trên kpi, cả 3 hợp lệ.
- Chưa apply lên cụm và chưa chạy Job thử. Chỉ apply khi người dùng xác nhận.
- Lịch 6 giờ với etcd và 02:00 với pg_dump, giữ 14 ngày, là đề xuất của Javis mà người dùng đã chấp nhận, chưa phải cấu hình người dùng tự đặt.

**Vì sao:** người dùng muốn bảo vệ PostgreSQL, etcd và các PVC trước khi vận hành tiếp.
**Áp dụng:** khi người dùng quay lại, hỏi trạng thái điền S3 và kết quả Job thử trước khi đề xuất thêm bước Longhorn.
