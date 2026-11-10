# Chỉ mục Wiki

Tri thức chưng cất trong MinFu. Đọc trang liên quan và citation nguồn; hướng dẫn/kế hoạch/snapshot tài liệu không thay cho trạng thái live.

## Argo CD và GitOps

- [[wiki/devops/Argo CD đa cluster|Argo CD đa cluster]]: Argo CD trung tâm, vòng đời cluster và kiểm tra đúng destination.
- [[wiki/devops/Quản lý kubeconfig nhiều cluster|Quản lý kubeconfig nhiều cluster]]: Merge, chuẩn hóa context và tránh ghi đè cấu hình nhiều cluster.
- [[wiki/devops/Phân quyền và credential Argo CD|Phân quyền và credential Argo CD]]: ServiceAccount, TLS và quy ước project local/default, remote/theo tên cluster.
- [[wiki/devops/ApplicationSet và GitOps đa cluster|ApplicationSet và GitOps đa cluster]]: Generator, destination từ values, bootstrap và kiểm tra template.

## Credential và certificate Kubernetes

- [[wiki/devops/Kubeconfig ServiceAccount cho FPT FKE|Kubeconfig ServiceAccount cho FPT FKE]]: Bootstrap token kubeconfig, RBAC, rotate/revoke và kiểm chứng độc lập.
- [[wiki/devops/Gia hạn certificate kubeconfig bằng kubeadm|Gia hạn certificate kubeconfig bằng kubeadm]]: Nhận dạng certificate, renew đúng file, bảo toàn multi-context và verify.

## Sentry và Kafka

- [[wiki/devops/Chẩn đoán pipeline ingest Sentry|Chẩn đoán pipeline ingest Sentry]]: Chẩn đoán theo tầng và phân biệt Kafka lag 0 với ingest khỏe.
- [[wiki/devops/Kafka OffsetOutOfRange trong Sentry|Kafka OffsetOutOfRange trong Sentry]]: Reset riêng topic, so earliest/latest và verify sau phục hồi.
- [[wiki/devops/Tăng throughput consumer Sentry|Tăng throughput consumer Sentry]]: Case 4 partition/4 process, cú pháp consumer và giới hạn scale.
- [[wiki/devops/Relay buffer đầy và HTTP 503|Relay buffer đầy và HTTP 503]]: Runbook lịch sử Relay 503/buffer; case đã closed theo xác nhận người dùng.

## Submariner và kết nối đa cluster

- [[wiki/devops/Kiến trúc Submariner đa VPC|Kiến trúc Submariner đa VPC]]: Thiết kế Broker/data plane, private subnet và HA gateway; hiện chưa triển khai.
- [[wiki/devops/CIDR và Globalnet cho Submariner|CIDR và Globalnet cho Submariner]]: Chia pool IP không overlap và điều kiện dùng Globalnet.
- [[wiki/devops/Triển khai và khám lỗi Submariner|Triển khai và khám lỗi Submariner]]: Requirements, deploy Broker/join, firewall và phân nhánh lỗi.
- [[wiki/devops/Lighthouse và service discovery đa cluster|Lighthouse và service discovery đa cluster]]: Export/import service, DNS liên cluster và nối với Argo CD.
- [[wiki/devops/Đo latency và MTU của Submariner|Đo latency và MTU của Submariner]]: Đo từng lớp, benchmark baseline và tách network khỏi application.

## Điều hướng

- [[wiki/_open-questions|Câu hỏi cần xác minh]]
- [[wiki/log|Nhật ký Wiki]]

## GitLab CI và build image

- [[GitLab Runner dùng Docker executor]]: Cấu hình runner `fsel-prod` theo bản người dùng cung cấp.
- [[wiki/devops/Cache build image với Docker và Buildah|Cache build image với Docker và Buildah]]: Nơi lưu và cách tái sử dụng cache trong mô hình hiện tại và phương án Buildah.

## Tự học
- [[devops/Vertical Pod Autoscaler (VPA)]] - ## Tóm tắt
Vertical Pod Autoscaler (VPA) tự đề xuất hoặc tự điều chỉnh `requests
- [[Lỗi No scopes requested khi cài Slack app]] - Slack báo "Invalid permissions requested / No scopes requested" khi cài app, khi
- [[Cấp kubeconfig theo namespace có duyệt admin]] - Cấp quyền kubeconfig cho dev nên dựa trên danh sách namespace được phép (whiteli
- [[Cookie secret của oauth2-proxy phải đúng 16, 24 hoặc 32 byte]] - oauth2-proxy từ chối `cookie_secret` không đúng độ dài và in thông báo `cookie_s
- [[Gọi API xuyên cluster qua gateway HTTPS mTLS]] - Khi hai cluster Kubernetes nằm ở nhà cung cấp cloud khác nhau, không nên giả địn
- [[Điều khiển và hỗ trợ lái trên VinFast VF 6]] - ## Chọn số và giữ xe

- Cụm chọn số có P, R, N và D; cần đạp phanh khi chuyển số
- [[Đổi tên Facebook Page]] - ## Các bước đổi tên

Trên máy tính, chuyển sang dùng Facebook với tư cách Trang,
- [[Solution .NET (.sln)]] - File `.sln` là solution, dùng để nhóm và quản lý các project liên quan trong một
