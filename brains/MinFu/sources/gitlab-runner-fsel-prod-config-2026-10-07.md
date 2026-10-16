---
type: source
source_kind: chat
status: unprocessed
created: 2026-10-07
processed_at: null
wiki_links: []
url: null
---

# GitLab Runner của fsel-prod

Nguồn: người dùng cung cấp qua Telegram ngày 2026-10-07. Theo người dùng, GitLab Runner được cài bằng Docker; mỗi lần pipeline chạy sẽ tạo một container tạm thời.

Lưu ý: credential trong `auth_config` đã được che khi lưu nguồn. Dòng `volumes` được giữ theo nội dung dán, gồm các khoảng trắng có thể do terminal tự xuống dòng; cần kiểm tra trên host trước khi dùng làm cấu hình thực thi.

```toml
# root@f8b324a728e4:/# cat /etc/gitlab-runner/config.toml
concurrent = 4
check_interval = 0
shutdown_timeout = 0
[session_server]
  session_timeout = 1800
[[runners]]
  privileged = true
  name = "runner-local"
  url = "https://gitlab.fsel.edu.vn"
  id = 89
  token = "xxx"
  token_obtained_at = 2024-09-18T07:57:13Z
  token_expires_at = 0001-01-01T00:00:00Z
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    MaxUploadedArchiveSize = 0
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    dns = ["8.8.8.8", "1.1.1.1"]
    memory = "4g"
    tls_verify = false
    auth_config = ["registry.fsel.edu.vn=<credential redacted>"]
    image = "mirror.gcr.io/library/docker:27"
    pull_policy = "always"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock", "/sencha/e                                                                                                                           xt:/sencha/ext", "/sencha/node_modules:/sencha/node_modules", "/detectAIvoice/mo                                                                                                                           del:/detectAIvoice/model"]
    shm_size = 0
    network_mtu = 0
```
