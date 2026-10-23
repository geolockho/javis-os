---
type: business
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Người dùng đã điền xong bản prompt cho công cụ cấp kubeconfig theo namespace cho dev (thực tế tính đến 2026-10-23, [[conversations/2026-10-23]]).

- Cluster cần hỗ trợ: 2, gồm fsel-prod (FKE, K8s 1.25) và fsel-local (K8s 1.34) (thực tế tính đến 2026-10-23, [[conversations/2026-10-23]]).
- Hiện dev chưa có cơ chế xác thực riêng, đang thêm kubeconfig vào Lens thủ công (thực tế tính đến 2026-10-23, [[conversations/2026-10-23]]).
- Mục tiêu thiết kế: web nhỏ, dev điền Name, Project, Expiration (ví dụ 1 month); quyền read-only; có bước duyệt, admin đăng nhập ở một tính năng ẩn để xem ai xin, namespace nào, quyền gì, khi nào và hết hạn khi nào (mục tiêu, [[conversations/2026-10-23]]).
- Vẫn chưa chốt: cách map team sang namespace, cách dev đăng nhập, nơi lưu request, và read-only có gồm Secret, logs hay exec không (cần xác minh, người dùng chưa trả lời, [[conversations/2026-10-23]]).
- Chưa có code, chưa chốt kiến trúc.
