---
superseded_by: mcp-local-may-ca-nhan-dung-mcp-2x-thieu-uv
type: decision
provenance: user
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
- Ngày 2026-10-12 người dùng dựng MCP server Python tại `D:\mcp-local\server.py` (venv `D:\mcp-local\.venv`), tên `may-ca-nhan`, có các tool run_command, read_file, write_file, list_dir và ghi audit log.
- Lỗi gặp phải: `mcp[cli]` bản 2.x đổi `FastMCP` thành `MCPServer`. Hướng đã chọn: ghim `mcp[cli]<2` và dùng `from mcp.server.fastmcp import FastMCP`.
- Dự kiến đấu vào Javis bằng `javis_add_mcp` với stdio, quyền full. Nguồn chạy bằng lệnh được thêm ở trạng thái TẮT, người dùng phải bật ở trang Kết nối.
- Trạng thái (thực tế tính đến 2026-10-12): chưa chạy được `mcp dev`, chưa đấu vào Javis.
**Áp dụng:** khi người dùng báo `mcp dev` chạy được thì đấu bằng javis_add_mcp. Nếu họ hỏi về file trên máy ngoài vault, nhắc là chưa đọc được cho tới khi MCP này đấu xong.


## Lịch sử
- [2026-10-12] Bị thay thế bởi [[mcp-local-may-ca-nhan-dung-mcp-2x-thieu-uv]] (user đổi thông tin).
