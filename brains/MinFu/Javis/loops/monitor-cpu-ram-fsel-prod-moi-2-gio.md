---
type: loop
name: Monitor CPU/RAM fsel-prod mỗi 2 giờ
slug: monitor-cpu-ram-fsel-prod-moi-2-gio
enabled: true
goal: custom
mode: full
interval_min: 120
workspace: vault
tools_profile: vault-safe
quiet_hours: ''
max_runs_per_day: 0
owner_chat: ''
notify: false
updated: '2026-10-14'
---

Giám sát CPU/RAM namespace fsel-prod, context fsel-prod. Dùng tool may-ca-nhan-2__run_command (PowerShell) chạy: kubectl --context fsel-prod -n fsel-prod get pods -o json (lấy requests CPU/memory từng container và tên pod) và kubectl --context fsel-prod -n fsel-prod top pods --no-headers (usage). Gộp theo service (bỏ hậu tố hash của pod), tính: số pod, tổng CPU/RAM request, tổng CPU/RAM usage, % usage/request. Ngưỡng: từ 80% là CẢNH BÁO, từ 90% là NGHIÊM TRỌNG; service không có request thì ghi 'không có request' chứ không tính %. Pod không có số liệu top thì ghi chú. Gửi kết quả bằng Slack (tool gửi tin nhắn) vào kênh C0C8RMMB7AN (Minh Phú Space): dòng đầu có tổng số pod, số service cảnh báo/nghiêm trọng; sau đó bảng ngắn các service vượt ngưỡng trước, rồi top service theo usage. Chỉ gửi Slack, không gửi Zalo. Chỉ chạy lệnh đọc, không thay đổi cụm. Nếu kubectl lỗi, gửi một tin báo lỗi vào cùng kênh.
