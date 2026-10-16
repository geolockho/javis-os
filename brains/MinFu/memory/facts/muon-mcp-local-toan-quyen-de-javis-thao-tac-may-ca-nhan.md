---
superseded_by: mcp-local-may-ca-nhan-dang-dung-do
type: decision
provenance: user
origin: javis-learned
created: 2026-10-12
updated: 2026-10-12
---
Ngày 2026-10-12 người dùng yêu cầu tạo một MCP mới trên máy cá nhân. Javis sẽ giao tiếp với MCP này để thao tác trên máy, và MCP có toàn quyền truy cập và chạy lệnh.

**Vì sao:** engine hiện tại của Javis (anthropic-api) không có Bash và không có tool Kubernetes. Vì vậy Javis chưa tự chạy được `kubectl` lên cụm kpi/kpi-uat để kiểm tra lỗi, ví dụ job etcd-snapshot.

**Hiện trạng (thực tế tính đến 2026-10-12):**
- Kho kết nối chưa có MCP Kubernetes, shell hay filesystem.
- Nguồn Minh Phú là connector Zalo Agent MCP, không liên quan Kubernetes, và đang không kết nối được.
- Javis đã đề xuất tự viết MCP server Python (FastMCP, stdio) tại `D:\mcp-local`, đấu bằng `javis_add_mcp` với quyền `full`. Nguồn chạy bằng lệnh sẽ được thêm ở trạng thái TẮT, người dùng phải bật ở trang Kết nối.
- Chưa xác nhận người dùng đã tạo hay đấu xong.

**Áp dụng:** khi cần kiểm tra cụm, chưa giả định Javis chạy được kubectl. Hỏi lại xem MCP đã được bật chưa trước khi hứa chạy lệnh.


## Lịch sử
- [2026-10-12] Bị thay thế bởi [[mcp-local-may-ca-nhan-dang-dung-do]] (user đổi thông tin).
