---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
source: [[sources/ci-templates-2026-10-07/README]]
---

# Cache build image với Docker và Buildah

## Cơ chế chung

Cả Docker và Buildah có thể tái dùng kết quả các bước build khi đầu vào phù hợp không đổi. Docker BuildKit kiểm tra cache theo lệnh và đầu vào của `COPY`/`ADD`; Buildah lưu intermediate images khi bật `--layers`. Đây là cơ chế cache layer, khác với cache thư mục tải gói trong `RUN --mount=type=cache`. [Docker cache invalidation](https://docs.docker.com/build/cache/invalidation/) [Buildah build](https://github.com/containers/buildah/blob/main/docs/buildah-build.1.md)

## Mô hình fsel-exam đã đọc

Thực tế theo snapshot CI local ngày 2026-10-07: `general.yml` comment `docker:dind` và `DOCKER_HOST`; template build gọi `docker build` rồi `docker push`. Runner được người dùng cung cấp có mount `/var/run/docker.sock`, nên với cấu hình này Docker CLI dùng builder của host. Chưa đối chiếu pipeline live trên GitLab. [[sources/ci-templates-2026-10-07/README]] [[gitlab-runner-fsel-prod-config-2026-10-07]] [[GitLab Runner dùng Docker executor]]

Vì builder ở host, cache layer và cache mount do builder giữ có thể còn sau khi job container bị xóa và được job sau trên cùng host tái sử dụng, tùy cache chưa bị dọn và đầu vào vẫn khớp. Template này không khai `cache:` hoặc xuất/nhập cache build qua registry; chỉ `docker push` image cuối, không đồng nghĩa xuất cache build cho runner khác. [[sources/ci-templates-2026-10-07/README]] [Docker cache storage](https://docs.docker.com/build/cache/backends/)

## Nếu đổi bước build sang Buildah

Docker executor vẫn tạo job container, còn Buildah build bên trong container. Buildah không dùng cache của Docker builder trên host. `buildah build --layers` lưu intermediate images trong storage của Buildah; nếu storage chỉ nằm trong container tạm, job sau không giữ được cache local đó. Có thể mount storage bền vững hoặc dùng `--layers --cache-from <repo> --cache-to <repo>` để pull/push cache qua registry. [Buildah build](https://github.com/containers/buildah/blob/main/docs/buildah-build.1.md) [[GitLab Runner dùng Docker executor]]

Buildah cũng hỗ trợ `RUN --mount=type=cache`: dữ liệu cache mount tồn tại qua các lần dùng khi storage tương ứng còn, nhưng không nên coi cache thư mục npm này là một phần của cache layer registry nếu chưa kiểm chứng bằng build thực tế. [Buildah run](https://github.com/containers/buildah/blob/main/docs/buildah-run.1.md) [Buildah build](https://github.com/containers/buildah/blob/main/docs/buildah-build.1.md)

## Quyết định còn mở

Người dùng đang đánh giá khả năng tối ưu cache khi cân nhắc Buildah; chưa có quyết định chuyển. Cần đo trên pipeline đại diện với build lạnh, build ấm trên cùng host và build ở host khác, gồm thời gian và dữ liệu truyền registry. [[memory/conversations/2026-10-07]]
