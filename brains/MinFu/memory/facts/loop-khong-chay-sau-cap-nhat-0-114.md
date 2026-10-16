---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
- Thực tế tính đến 2026-10-14: server Javis tự cập nhật từ 0.105 lên 0.114 lúc 08:53. Lần chạy cuối của loop Tổng hợp kiến thức là 09:55 ngày 09/10. Loop monitor CPU/RAM fsel-prod chưa từng chạy thành công.
- Người dùng đã đăng nhập lại Claude và khởi động lại Javis từ terminal thường (cách 1). Server chạy lại lúc 11:04, PID 21624.
- Sau khi khởi động lại, loop có ghi lỗi vào log (vì `self_improve.py` có bản vá chưa commit, sửa lúc 10:52): monitor-cpu-ram-fsel-prod-moi-2-gio (manual 11:04) và tong-hop-kien-thuc (scheduled 11:04, manual 11:05) đều báo `Lỗi: Claude CLI is not installed` / `Claude CLI chưa cài`.
- Lỗi phát ra ở `self_improve.py:996`, chỗ `gcli.is_available()` trả false. Trong khi đó `/health` của cùng tiến trình trả `claude_cli_available: true` (đường dẫn `...\npm\claude.CMD`). Vậy chỉ còn khả năng `_SDK_OK = False`: `import claude_agent_sdk` lỗi lúc nạp module và bị `except Exception` nuốt mất (`claude_sdk_engine.py:30-38`).
- Chạy ngoài server bằng cùng `.venv` thì không tái hiện được: SDK 0.2.116 import tốt, `pip check` sạch.
- Bước tiếp đã đề xuất, đang chờ người dùng đồng ý vì sửa mã server: thêm log ngoại lệ ra stderr ở nhánh except dòng 37-38 của `claude_sdk_engine.py`, khởi động lại, bấm Run now, rồi đọc `javis.log` để biết lỗi import thật.
