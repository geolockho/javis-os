---
type: reference
provenance: assistant
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
Theo mã `self_improve.py` mà Javis đọc ngày 2026-10-14, `tools_profile` của loop chỉ có hai giá trị hợp lệ.

- `vault-safe`: có các MCP do Javis quản lý, gồm `may-ca-nhan-2` (kubectl) và Slack. Mode `full` không chặn hành động ra ngoài.
- `code`: mở Bash nhưng cho 0 MCP, nên loop không gọi được `run_command` lẫn Slack.
- Loop monitor CPU/RAM fsel-prod cần kubectl và Slack nên phải giữ `vault-safe`.
- Đổi sang `code` sẽ làm loop này hỏng.
