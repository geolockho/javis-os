---
type: business
provenance: user
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---
Người dùng xác nhận `D:\FSEL\Ci-Templates` là nơi chứa CI. Cấu trúc `.gitlab-ci.yml` thông thường include `/general.yml`, `/nexus-npm.yml`, `/build-image-gitlab-registry.yml` từ `ci-templates/build-docker-images` và `fsel/web/fsel-exam.yaml` từ `ci-templates/gitlab-ci-projects`; các include được cung cấp đều dùng `ref: master`.
