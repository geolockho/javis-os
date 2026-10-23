---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Người dùng chốt dựng công cụ cấp kubeconfig theo namespace bằng chính Javis: tạo cả 3 năng lực gồm agent `tl-ra-soat-rbac`, skill `kiem-thu-kubeconfig-dev` và workflow `dung-cong-cu-cap-kubeconfig` (thực tế tính đến 2026-10-23, [[conversations/2026-10-23]]). Sau khi code xong, người dùng muốn push lên repo GitLab trong [[repo-kubeconfig-generator]] (mục tiêu, [[conversations/2026-10-23]]).

**Vì sao:** người dùng muốn tận dụng partner, skills và workflow của Javis cho việc này ([[conversations/2026-10-23]]).

**Áp dụng:** tính đến 2026-10-23 chưa tạo file nào. Trước khi tạo, hỏi lại các điểm còn mở: namespace thử trên fsel-local, nơi đặt code, workflow có dừng chờ duyệt kiến trúc không, và cách push (nhánh riêng hay main, cùng quyền ghi). Không coi công cụ là đã xong.
