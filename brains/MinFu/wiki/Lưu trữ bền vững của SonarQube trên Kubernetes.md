---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-11-10
updated: 2026-11-10
source: [[conversations/2026-11-10]]
---
PostgreSQL lưu dữ liệu SonarQube như project, cấu hình và lịch sử phân tích; PVC của pod SonarQube có thể giữ chỉ mục tìm kiếm để giảm thời gian khởi động lại. [[Tài liệu lưu trữ SonarQube]]

Nếu chỉ mục nằm trên ổ tạm, pod tạo lại sẽ mất chỉ mục và SonarQube cần dựng lại từ database; vì vậy database bền vững và được sao lưu là phần cốt lõi. [[Tài liệu lưu trữ SonarQube]]
