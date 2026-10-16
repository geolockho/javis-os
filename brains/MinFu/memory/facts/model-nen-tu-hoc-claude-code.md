---
superseded_by: chuyen-model-nen-sang-haiku
type: preference
provenance: user
origin: javis-learned
created: 2026-10-08
updated: 2026-10-08
---
Ngày 2026-10-08, người dùng cho biết khi thêm Claude Code thì Javis tự dùng nó cho tác vụ nền (vòng tự học, loop/schedule). Người dùng hỏi chỗ đổi model chạy nền và cân nhắc dùng một model Ollama để tổng hợp kiến thức thay thế. Chưa chốt model nào; Javis gợi ý `qwen3:30b` nhưng đó chỉ là đề xuất.

Cùng ngày, khi được hỏi phạm vi đổi, người dùng chốt: **chỉ đổi model cho việc nền**, không đổi model của chat.

Vòng tự học bằng Claude Opus từng tiêu khoảng 608 nghìn token nền trong buổi sáng 2026-10-08, chủ yếu là cache; panel Mức dùng sau đó ghi khoảng 1,4M token Claude Code (opus-5-5, 23 lượt) ở mục Background.

**Vì sao:** muốn giảm chi phí/hạn mức Claude cho việc nền.
**Áp dụng:** khi hướng dẫn đổi model, chỉ chỉnh model nền (nút Change model ở mục Background hoặc trang Models), không đụng model chat chính.


## Lịch sử
- [2026-10-08] Bị thay thế bởi [[chuyen-model-nen-sang-haiku]] (user đổi thông tin).
