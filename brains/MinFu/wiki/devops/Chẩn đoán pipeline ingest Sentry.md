---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Sentry Self-Hosted 24.1.0", "Sentry ingest troubleshooting", "Kafka lag zero"]
source: ["[[sources/readme/sentry-self-hosted-ingest-troubleshooting]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Chẩn đoán pipeline ingest Sentry

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận case Sentry đã xử lý được và `closed`. Các sự cố/503/drop và thông số bên dưới là lịch sử trong nguồn, không tiếp tục coi case này đang mở. Ngày đo cũ và chi tiết biện pháp sửa cuối cùng chưa được cung cấp; lần cập nhật này không kiểm tra live. [[sources/readme/open-questions-answers-2026-10-07]]

Trang này tổng hợp case Sentry self-hosted 24.1.0 có ingest chậm, consumer restart, Kafka OffsetOutOfRange và Relay 503. Nguồn không ghi ngày đo; các kết quả là snapshot lịch sử trong tài liệu, không phải trạng thái live ngày ingest 2026-10-07. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Sơ đồ và cách đọc tín hiệu

Luồng nguồn mô tả SDK -> Nginx -> Relay -> Kafka ingest-events -> events-consumer -> Snuba/ClickHouse/Postgres/các bước sau -> UI. Nginx nhận HTTP, Relay validate/normalize/process envelope và produce Kafka; worker xử lý background jobs. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

- CURRENT-OFFSET đứng, LOG-END-OFFSET tăng, lag tăng: kiểm tra phía consumer/assignment. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- CURRENT-OFFSET=LOG-END-OFFSET, lag 0, cả hai offset đứng: topic không có message mới trong khoảng quan sát; phải kiểm tra SDK/Nginx/Relay/Kafka producer, không kết luận ingest đã khỏe. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- POST envelope trả 503 cùng log Relay buffer capacity exceeded: case ghi nhận drop trước Kafka; lag consumer có thể 0 vì đầu vào Kafka đã ngừng. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- OffsetOutOfRange/requested offset not available: so committed với earliest còn giữ; xem [[Kafka OffsetOutOfRange trong Sentry]]. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Diễn biến case theo nguồn

Host ban đầu khoảng 16 CPU, load 23,75/23,35/22,36, RAM/swap chịu áp lực; sau tăng tài nguyên nguồn ghi memory limit nhìn từ container 31,39 GiB. Topic tăng 1 -> 4 partition và consumer 1 -> 4 process, lag từng giảm 1.813 -> 144 rồi có lúc 0. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Nguồn ghi events-consumer CPU 65,61%, RAM 676,8 MiB; worker CPU 1.474,08% và RAM 3,204 GiB. Relay lúc lỗi CPU 10,43%, RAM 143,9 MiB; số thấp này là một snapshot, chưa chứng minh mọi dependency hay processing nội bộ không bị nghẽn. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Đã làm và còn thiếu ở thời điểm tài liệu cũ

Nguồn ghi đã reset ingest-events về latest, sửa offset invalid, tăng partition/process và buffer Relay 1.000 -> 10.000. Tuy vậy Relay tiếp tục đầy buffer, Nginx có 503 và envelope bị drop; throughput input và bottleneck nội bộ vẫn chưa xác định. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Quy trình kiểm tra tái dùng

1. Ghi thời điểm và cùng cửa sổ đo cho container restart/OOM, host CPU/RAM/swap, Kafka lag/end offset, Nginx status, Relay errors. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
2. So offset qua hai snapshot; đối chiếu traffic envelope theo project, không chỉ lấy một lần lag=0. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
3. Phân loại lỗi trước Kafka, trong consumer hay downstream rồi chọn nhánh riêng; không dùng tăng retention/buffer/partition thay đo bottleneck. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Lệnh đọc trạng thái tham chiếu; tên container theo case, cần khớp môi trường thực tế: [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

```bash
docker compose ps
docker stats --no-stream
docker compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ingest-consumer --describe
docker compose logs --since=5m relay
docker compose logs --since=5m nginx
```

Liên quan: [[Kafka OffsetOutOfRange trong Sentry]], [[Tăng throughput consumer Sentry]], [[Relay buffer đầy và HTTP 503]].
