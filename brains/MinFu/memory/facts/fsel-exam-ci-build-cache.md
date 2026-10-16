---
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---
Tính đến 2026-10-07, Javis phân tích bản CI local của `fsel-exam`: cấu hình DinD bị comment, job gọi `docker build` và `docker push`, còn runner mount `/var/run/docker.sock`. Vì vậy, theo cấu hình đã đọc, job dùng Docker daemon của host. Cache layer và cache mount npm có thể tồn tại qua các job trên cùng host; template này không khai báo `cache:` hoặc `--cache-from/--cache-to`. Chưa đối chiếu pipeline đang chạy trên GitLab. Nguồn đối chiếu: `sources/ci-templates-2026-10-07/README` và `sources/gitlab-runner-fsel-prod-config-2026-10-07`.

Người dùng đang đánh giá hiệu quả cache của mô hình Docker hiện tại so với Buildah. Chưa có quyết định chuyển sang Buildah. [[memory/conversations/2026-10-07]]
