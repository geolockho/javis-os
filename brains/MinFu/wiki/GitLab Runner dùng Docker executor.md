---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
source: [[conversations/2026-10-07]]
---
## Cấu hình tham khảo

Trong cấu hình `fsel-prod` do người dùng cung cấp ngày 2026-10-07, GitLab Runner được cài bằng Docker, dùng Docker executor và tạo container tạm cho mỗi lần chạy pipeline (thực tế theo bản cấu hình được gửi, chưa xác minh trạng thái đang chạy). [[gitlab-runner-fsel-prod-config-2026-10-07]]

Runner đặt `concurrent = 4`, giới hạn bộ nhớ container là `4g`, dùng image `mirror.gcr.io/library/docker:27` và đặt `pull_policy = "always"` (thực tế theo bản cấu hình được gửi ngày 2026-10-07). [[gitlab-runner-fsel-prod-config-2026-10-07]]

Cấu hình bật `privileged = true` và mount `/var/run/docker.sock` vào container (thực tế theo bản cấu hình được gửi ngày 2026-10-07). [[gitlab-runner-fsel-prod-config-2026-10-07]]

Các đường dẫn mount trong bản dán có khoảng trắng xen giữa tên thư mục; cần đối chiếu cấu hình trên host trước khi dùng lại (cần xác minh). [[gitlab-runner-fsel-prod-config-2026-10-07]]
