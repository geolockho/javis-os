---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-11-10
updated: 2026-11-10
source: [[conversations/2026-11-10]]
---
Nếu container không khai báo request hoặc limit cho `ephemeral-storage`, request được tính là 0 và container không có limit riêng, trừ khi chính sách như `LimitRange` gán giá trị mặc định. [[Tài liệu Kubernetes]]

Container vẫn dùng dung lượng đĩa trên node cho log, lớp ghi và `emptyDir`; pod có thể bị evict khi node thiếu dung lượng. [[Tài liệu Kubernetes]]

Trong values của SonarQube chart phiên bản `2026.5.1004`, request mặc định là `1536M` và limit là `512000M`; đây là cấu hình tài nguyên, không phải dung lượng ổ đĩa được cấp sẵn. [[Values chart SonarQube 2026.5.1004]]
