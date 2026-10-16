---
superseded_by: mcp-local-may-ca-nhan-da-dau-vao-javis-dang-tat
type: decision
provenance: user
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
- Ngày 2026-10-12, người dùng chốt dùng mcp 2.x cho server `D:\mcp-local\server.py` (import `from mcp.server.mcpserver import MCPServer`), không ghim về 1.x.
- Chạy `.\.venv\Scripts\mcp dev server.py` thì Inspector khởi động, nhưng nó gọi `uv run --with mcp==2.3.0 mcp run server.py` và báo `'uv' is not recognized` (thực tế tính đến 2026-10-12). Nghĩa là máy chưa cài `uv` hoặc `uv` chưa có trong PATH.
- Chưa xác nhận server tự chạy được. Cần thử `.\.venv\Scripts\python server.py` hoặc cài uv để Inspector chạy.
- Chưa đấu vào Javis. Kế hoạch là dùng `javis_add_mcp` với stdio trỏ tới `D:\mcp-local\.venv\Scripts\python.exe` và `server.py`. Nguồn đấu bằng lệnh sẽ ở trạng thái tắt, người dùng bật ở trang Kết nối. Mức quyền dự kiến là full, đang chờ người dùng xác nhận.
- **Vì sao:** người dùng nói rõ muốn dùng bản 2.x.
- **Áp dụng:** không đề xuất ghim `mcp<2` nữa. Khi hỗ trợ tiếp, bắt đầu từ việc cài uv hoặc chạy trực tiếp bằng python.


## Lịch sử
- [2026-10-12] Bị thay thế bởi [[mcp-local-may-ca-nhan-da-dau-vao-javis-dang-tat]] (user đổi thông tin).
