---
superseded_by: mcp-local-may-ca-nhan-da-bat-va-hoat-dong
type: decision
provenance: assistant
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
- Ngày 2026-10-12 người dùng báo đã cài xong uv. File Inspector đính kèm cho thấy server `D:\mcp-local\server.py` (mcp 2.3.0) kết nối `Connected`, và `tools/list`, `resources/list`, `prompts/list` đều trả OK.
- Javis đã đấu nguồn `may-ca-nhan` bằng `javis_add_mcp` (stdio). Mục đúng có mã `bfcccb6fa672`, lệnh `D:/mcp-local/.venv/Scripts/python.exe D:/mcp-local/server.py`. Mục này **đang tắt**, quyền **readonly** (mặc định). Người dùng cần tự bật ở trang Kết nối.
- Mục trùng mã `7bd598f88cb5` bị sai lệnh `D:mcp-localserver.py` (mất dấu `\`), cần xoá.
- Mục **PHUHM-OFFICE** lỗi (`McpHttpError`, rồi `FileNotFoundError: WinError 2`) do người dùng dán nhầm link Inspector `127.0.0.1:6274`, vốn không phải MCP server, và điền ô Command chỉ có `server.py`. Cách sửa: chọn Run a command, Command là `python.exe` của venv, Arguments là `server.py`. Cũng có thể xoá mục này.
- Quyền full chưa được người dùng xác nhận nên Javis không tự nâng.
- Chưa gọi thử tool nào của nguồn này để kiểm chứng.
- Trạng thái tính đến 2026-10-12.


## Lịch sử
- [2026-10-12] Bị thay thế bởi [[mcp-local-may-ca-nhan-da-bat-va-hoat-dong]] (user đổi thông tin).
