---
superseded_by: loop-khong-chay-sau-cap-nhat-0-114
type: business
provenance: user
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
- Ngày 2026-10-14 người dùng bật công tắc **AI tự vận hành** bằng giao diện ở trang **Việc** (Kanban). Trang Scheduled không có công tắc này, chỉ có nút on/off từng loop, + Add job và Stop the running round.
- `Javis/kanban.json` giờ ghi `"orchestration": "auto"`. Lúc người dùng tự sửa tay file thành `on` thì không có tác dụng, vì file này chỉ là bản xuất từ `kanban.sqlite3`.
- Thực tế tính đến 2026-10-14: `loop-state.json` của loop monitor CPU/RAM fsel-prod vẫn chưa có `last_run` và `loop-log` chưa có file mới. Việc bấm Run now sau khi bật chưa được xác nhận.
- Việc cần làm tiếp: bấm Run now lại, rồi đọc `loop-state.json` và `loop-log` để kiểm chứng. Kubectl và Slack trong loop vẫn chưa được kiểm chứng.


## Lịch sử
- [2026-10-14] Bị thay thế bởi [[loop-khong-chay-sau-cap-nhat-0-114]] (user đổi thông tin).
