---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-11-10
updated: 2026-11-10
source: [[conversations/2026-11-10]]
---
Kubernetes không tự đặt một dung lượng cố định cho `ephemeral-storage` khi không có request hoặc limit, trừ khi chính sách namespace gán giá trị mặc định. [[Tài liệu Kubernetes về quản lý tài nguyên container]]

Container vẫn dùng dung lượng đĩa trên node cho log, lớp ghi và `emptyDir`; pod có thể bị evict khi node thiếu dung lượng. [[Tài liệu Kubernetes về quản lý tài nguyên container]]

Trong chart SonarQube `2026.5.1004`, values mặc định khai báo request `1536M` và limit `512000M`; bỏ các giá trị này khỏi file override không đồng nghĩa với việc bỏ mặc định của chart. [[Values chart SonarQube 2026.5.1004]]

Limit là giới hạn sử dụng được khai báo, không phải dung lượng ổ đĩa được cấp sẵn cho pod. [[Tài liệu Kubernetes về quản lý tài nguyên container]]
