---
type: reference
provenance: assistant
origin: javis-learned
created: 2026-10-29
updated: 2026-10-29
---
Thực tế được phát hiện ngày 2026-10-28: sau khi cài Javis chuyển từ `D:\private01\javis-os` sang `D:\javis-os`, database hội thoại vẫn lưu brain của 15 phiên web cũ bằng đường dẫn cũ (từ 08/10 đến 11:20 ngày 28/10). Bộ lọc `_brain_keys` trong `server/main.py` chỉ khớp đường dẫn hiện tại, nên 15 phiên không hiện trên thiết bị nào dù dữ liệu chưa mất. Bốn phiên mới hơn từ 14:05 ghi brain là `.`. Lúc ghi nhớ, chưa đổi dữ liệu DB; phương án đề xuất là sao lưu DB rồi cập nhật cột `brain` của 15 phiên, chờ người dùng đồng ý.