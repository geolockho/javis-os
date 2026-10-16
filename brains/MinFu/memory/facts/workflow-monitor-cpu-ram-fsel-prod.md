---
superseded_by: loop-monitor-cpu-ram-fsel-prod-da-dung
type: business
provenance: user
origin: javis-learned
created: 2026-10-13
updated: 2026-10-13
---
**Mục tiêu (chưa dựng):** một workflow chạy mỗi 2 giờ, đọc context fsel-prod, namespace fsel-prod, rồi báo:
- CPU và RAM usage, so với request, theo từng service.
- Số lượng pod đang chạy.
- Alert khi usage vượt ngưỡng so với request hoặc số pod bất thường.

**Phạm vi:** chỉ đọc, không đổi cấu hình cụm.

**Trạng thái:** chưa có ngưỡng alert và chưa có kênh nhận. Nguồn số liệu từ kubectl đã đọc được trong hội thoại ngày 2026-10-13.


## Lịch sử
- [2026-10-14] Bị thay thế bởi [[loop-monitor-cpu-ram-fsel-prod-da-dung]] (user đổi thông tin).
