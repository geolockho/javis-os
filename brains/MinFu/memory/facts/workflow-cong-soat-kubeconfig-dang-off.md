---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Ngày 2026-10-23 Javis đã tạo agent `tl-ra-soat-rbac`, skill `kiem-thu-kubeconfig-dev` và workflow `dung-cong-cu-cap-kubeconfig` (trạng thái off) để soát và kiểm kubeconfig-generator. Workflow chạy tuần tự `tl-phan-bien`, rồi `tl-ra-soat-rbac`, rồi `tl-thu-ky`, và chạy hai lần: trước khi viết code và sau khi code xong. Đây là cổng soát, còn code, duyệt và kiểm thử làm trong chat [[conversations/2026-10-23]].

**Thực tế tính đến 2026-10-23:** cổng soát lần 1 chưa chạy, cổng soát lần 2 chưa chạy, và người dùng chưa bật workflow. Workflow chỉ chạy khi công tắc "AI tự vận hành" ở trang Việc được bật. Agent chạy nền không ghi được vào `D:\FSEL`, nên mọi việc ghi code đều làm trong chat.

**Vì sao:** Người dùng yêu cầu RBAC phải được soát lại trước khi push, và lỗi mức Nghiêm trọng hoặc Cao phải sửa xong mới push. Agent nền không dừng giữa chừng được, nên không dùng nó để viết code hay để chờ duyệt.

**Áp dụng:** Trước khi push kubeconfig-generator, chạy cổng soát lần 2 bằng cách bật workflow hoặc gọi `tl-ra-soat-rbac` trong chat, rồi báo kết quả cho người dùng. Không bật "AI tự vận hành" hay tự apply RBAC lên cluster nếu người dùng chưa giao rõ. Liên quan: [[dung-cong-cu-kubeconfig-bang-javis]], [[tien-do-kubeconfig-generator-sau-cach-b]].
