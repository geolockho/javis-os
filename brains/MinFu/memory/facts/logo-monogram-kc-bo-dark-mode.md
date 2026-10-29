---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-29
updated: 2026-10-29
---
Ngày 2026-10-29 user chọn logo 3 (monogram kc) cho kubeconfig-generator và yêu cầu bỏ dark mode, giao diện chỉ còn bản sáng [[conversations/2026-10-29]].

Thay đổi nằm trong app/templates/base.html: bỏ bộ màu tối, nút chuyển theme và script lưu theme. Logo kc được dùng cho cả thanh nav và favicon.

- Commit 37a712e đã push lên origin/main (theo báo cáo của Javis, chưa mở GitLab kiểm) (thực tế tính đến 2026-10-29).
- Chưa render trang trên trình duyệt (cần xác minh).
- Javis hiểu là bỏ luôn nút chuyển. Nếu user chỉ muốn ẩn nút nhưng giữ bản tối làm mặc định thì chưa xác nhận (cần xác minh).
- Pod trên cluster vẫn chạy image cũ cho tới khi build và rollout image mới (thực tế tính đến 2026-10-29).

**Vì sao:** user muốn giao diện đơn giản, một bản sáng và logo gọn để làm favicon [[conversations/2026-10-29]].

**Áp dụng:** khi sửa giao diện kubeconfig-generator, giữ bản sáng và logo kc, không khôi phục dark mode trừ khi user yêu cầu lại.
