---
type: reference
provenance: source
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
- Ngày 2026-10-12 người dùng xác nhận đã bật nguồn MCP `may-ca-nhan` (mã `bfcccb6fa672`, lệnh `D:/mcp-local/.venv/Scripts/python.exe D:/mcp-local/server.py`). Trong Javis nguồn này hiện tên `may-ca-nhan-2`.
- Các tool: `run_command`, `list_dir`, `read_file`, `write_file`. Đã kiểm chứng `run_command` (PowerShell, exit 0) và `list_dir`. Chưa thử `read_file` và `write_file`.
- Máy là PHUHM-OFFICE, user `phuhm-office\phuhm`, thư mục làm việc mặc định `D:\private01\javis-os`.
- `kubectl get nodes` chạy được qua nguồn này. Context hiện tại là `kpi`, 9 node Ready (thực tế tính đến 2026-10-12).
- Quyền khi đấu là readonly. Chưa kiểm chứng việc ghi hay lệnh thay đổi hệ thống có bị chặn không.
- Còn hai mục lỗi trên trang Kết nối cần dọn: PHUHM-OFFICE (đấu bằng link tới Inspector hoặc lệnh sai) và mục trùng `7bd598f88cb5` (lệnh sai do mất dấu `\`).
- Bẫy: form "Run a command" của Javis coi cả chuỗi ở ô Command là một tên chương trình, nên không gộp được Python và `server.py` vào một ô (lỗi WinError 2). Dùng ô "Paste a config" dạng JSON `mcpServers` với `command` và `args` tách riêng. Link `http://127.0.0.1:6274` là giao diện MCP Inspector, không phải MCP server.
