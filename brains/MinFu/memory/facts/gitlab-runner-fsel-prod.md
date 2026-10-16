---
type: reference
provenance: user
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---
Theo cấu hình người dùng cung cấp ngày 2026-10-07, GitLab Runner của fsel-prod chạy bằng Docker, dùng Docker executor và tạo container tạm cho job. Runner `runner-local` có `concurrent = 4`, image mặc định `mirror.gcr.io/library/docker:27`, `pull_policy = "always"`, `privileged = true`, giới hạn bộ nhớ `4g` và mount `/var/run/docker.sock` từ host. Đây là bản cấu hình được cung cấp, chưa xác minh trực tiếp trên hệ thống đang chạy. Không lưu giá trị credential trong `auth_config`. [[conversations/2026-10-07]]
