---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
source: [[conversations/2026-10-23]]
---
Cấp quyền kubeconfig cho dev nên dựa trên danh sách namespace được phép (whitelist) thay vì group GitLab, vì dev thường được thêm vào project chứ không vào group [[conversations/2026-10-23]]. Người dùng đã yêu cầu bỏ điều kiện group và đã duyệt kiến trúc này [[conversations/2026-10-23]]. Mỗi yêu cầu vẫn phải qua bước admin duyệt, và namespace bị gỡ khỏi danh sách thì yêu cầu đang chờ không được duyệt nữa [[conversations/2026-10-23]]. Whitelist cũng chặn các namespace hệ thống, vì công cụ chỉ cấp quyền ở namespace đã có RoleBinding (cần xác minh: phạm vi chặn chưa kiểm trên cluster thật) [[conversations/2026-10-23]].
