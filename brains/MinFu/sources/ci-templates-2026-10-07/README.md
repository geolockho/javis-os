---
type: source
source_kind: own-note
status: unprocessed
created: 2026-10-07
processed_at: null
wiki_links: []
url: null
---

# Snapshot CI templates

Người dùng chỉ định `D:\FSEL\Ci-Templates` là nơi chứa CI và yêu cầu lưu vào source ngày 2026-10-07 lúc 14:00 (Asia/Ho_Chi_Minh).

Thư mục `raw/` là bản sao nguyên nội dung của **91 file** trong đường dẫn trên tại lúc lưu. Đã so SHA-256 từng file với bản gốc sau khi sao chép: **91/91** khớp. Tổng dung lượng file nguồn là **106017 byte**. Đây là snapshot local, không xác nhận các project/ref `master` trên GitLab đang có nội dung giống bản local hoặc pipeline đang chạy theo bản này.

Ví dụ `.gitlab-ci.yml` được người dùng cung cấp:

```yaml
include:
  - project: 'ci-templates/build-docker-images'
    ref: master
    file: '/general.yml'

  - project: 'ci-templates/build-docker-images'
    ref: master
    file: '/nexus-npm.yml'

  - project: 'ci-templates/build-docker-images'
    ref: master
    file: '/build-image-gitlab-registry.yml'

  - project: 'ci-templates/gitlab-ci-projects'
    ref: master
    file: fsel/web/fsel-exam.yaml
```
