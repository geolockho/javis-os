---
type: business
provenance: user
origin: javis-learned
created: 2026-10-14
updated: 2026-10-14
---
- Người dùng chốt ngưỡng: usage từ 80% request là cảnh báo, từ 90% là nghiêm trọng. [[conversations/2026-10-14]]
- Loop `Javis/loops/monitor-cpu-ram-fsel-prod-moi-2-gio.md` đã được tạo ngày 2026-10-14. Lúc tạo nó ở trạng thái tắt, người dùng cần bấm Bật ở tab Việc; mục lục năng lực hiện ghi là bật (cần xác minh). [[conversations/2026-10-14]]
- Cách làm: dùng `kubectl` qua nguồn `may-ca-nhan-2`, context `fsel-prod`, namespace `fsel-prod`. Gộp pod theo service, tính số pod, tổng request, tổng usage và % usage trên request. Service không có request thì ghi "không có request" và không tính %. Service vượt ngưỡng được đưa lên đầu. Nếu kubectl lỗi thì gửi một tin báo lỗi vào cùng kênh. [[conversations/2026-10-14]]
- Kiểm tra lúc dựng (thực tế tính đến 2026-10-14): cụm có metrics-server. Namespace `fsel-prod` có 86 pod, `kubectl top pods` trả 84 dòng, nên 2 pod chưa có số liệu usage. [[conversations/2026-10-14]]
- Chưa chạy thử cả loop và chưa có bản thống kê nào gửi lên Slack (thực tế tính đến 2026-10-14). [[conversations/2026-10-14]]

**Vì sao:** người dùng cần theo dõi tài nguyên fsel-prod đều đặn. **Áp dụng:** khi được hỏi về monitor fsel-prod, kiểm tra trạng thái bật của loop và chạy thử một lượt để xác nhận tin nhắn trên Slack.
