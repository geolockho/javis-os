---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
Thực tế tính đến 2026-10-14, các lần chạy loop `monitor-cpu-ram-fsel-prod-moi-2-gio` đều failed với chuỗi lỗi:
- `Claude CLI chưa cài` / `Claude CLI is not installed` / `Claude engine unavailable (engine=aux_engine._ApiAuxEngine; sdk_available=True; cli_path=...\npm\claude.CMD)`.
- Sau đó chạy bằng Ollama (Local) model `gemma3:4b`: lỗi `does not support tools`, rồi `model 'gemma3:4b' not found`, rồi `request (14498 tokens) exceeds the available context size (4096 tokens)`.
- Prompt loop (kèm tool kubectl, Slack và ngữ cảnh brain) khoảng 14.5k token mỗi lần chạy.
- Javis đã gợi ý: đặt `OLLAMA_CONTEXT_LENGTH=16384` (biến môi trường user trên Windows rồi mở lại Ollama) và đổi sang model có hỗ trợ tool như qwen3 hoặc llama3.1, hoặc dùng model API. Người dùng chưa chốt phương án (cần xác minh).
- Lần chạy thủ công lúc 13:33 ngày 2026-10-14 không lỗi context nữa nhưng bị `ReadTimeout` rồi bị huỷ vì quá hạn (Ollama local không trả lời kịp với prompt khoảng 14,5k token). Javis khuyến nghị dùng model API cho loop này vì cần gọi tool kubectl và Slack.
- Ngày 2026-10-14 người dùng đã tắt báo kết quả loop này về khung chat (`notify: false`, xoá `owner_chat`), nên lỗi chạy tự động sẽ không hiện ở chat nữa; xem [[tat-bao-ket-qua-loop-monitor-ve-chat]].

Liên quan: [[loop-khong-chay-sau-cap-nhat-0-114]].
