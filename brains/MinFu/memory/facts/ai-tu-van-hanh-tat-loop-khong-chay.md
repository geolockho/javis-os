---
superseded_by: ai-tu-van-hanh-da-bat-loop-monitor-chua-xac-nhan-chay
type: reference
provenance: assistant
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
Thực tế tính đến 2026-10-14: `Javis/kanban.json` của brain MinFu có `"orchestration": "off"`, tức công tắc **AI tự vận hành** ở trang Việc đang tắt.

- Khi tắt, bấm Run now chỉ xếp hàng, không thực thi. Chạy theo chu kỳ cũng không chạy.
- Loop `monitor-cpu-ram-fsel-prod` vẫn ghi never run và không có `last_run` trong `loop-state.json`.
- Loop `tong-hop-kien-thuc` đứng im từ 2026-10-09 dù báo due now.
- `owner_chat` của loop monitor đã trỏ về khung chat web hiện tại. Kênh Slack là C0C8RMMB7AN.
- Javis không có tool để bật công tắc này. Người dùng phải bật bằng tay ở trang Việc.
- Việc cần kiểm chứng: sau khi bật, bấm Run now và xem kubectl cùng Slack có chạy trong loop không. Chưa kiểm chứng được.


## Lịch sử
- [2026-10-14] Bị thay thế bởi [[ai-tu-van-hanh-da-bat-loop-monitor-chua-xac-nhan-chay]] (user đổi thông tin).
