---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["events-consumer processes", "ingest-events partitions", "Consumer parallelism"]
source: ["[[sources/readme/sentry-self-hosted-ingest-troubleshooting]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Tăng throughput consumer Sentry

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận case Sentry đã xử lý được và `closed`. Các sự cố/503/drop và thông số bên dưới là lịch sử trong nguồn, không tiếp tục coi case này đang mở. Ngày đo cũ và chi tiết biện pháp sửa cuối cùng chưa được cung cấp; lần cập nhật này không kiểm tra live. [[sources/readme/open-questions-answers-2026-10-07]]

Trang này ghi case tăng song song events-consumer để xử lý backlog Kafka của Sentry 24.1.0. Các số là kết quả tài liệu không có ngày đo, chưa kiểm tra live; không phải cấu hình mặc định cho mọi Sentry. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Thay đổi trong case

Ban đầu ingest-events có 1 partition, replication factor 1; consumer không cấu hình processes. Nguồn ghi đã tăng lên 4 partition và chạy 4 processes, group đọc đủ partition 0..3. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Cú pháp nguồn nhấn mạnh `--processes` số nhiều và dấu `--` phân tách subcommand option: [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

```yaml
events-consumer:
  <<: *sentry_defaults
  command: run consumer ingest-events --consumer-group ingest-consumer -- --processes 4
```

Nguồn recreate consumer sau sửa compose, kiểm tra `.Config.Cmd` bằng docker inspect. Chuỗi expected gồm run/consumer/ingest-events/--consumer-group/ingest-consumer/--/--processes/4, không suy file compose đã được áp dụng nếu chưa inspect process. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Kết quả và giới hạn

Lag từng giảm 1.813 -> 144 và có thời điểm 0; nguồn kết luận consumer bắt kịp backlog ở một số thời điểm. Tăng partition không giảm trực tiếp lại được và có thể ảnh hưởng ordering theo key; không tăng tiếp tùy tiện. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Replication factor vẫn 1 và case ghi single broker, nên tăng partition không tạo HA broker. Worker dùng gần 14,7 core trong snapshot và có khả năng tranh tài nguyên; cần đo lại host/downstream khi scale. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Consumer nhanh hơn không sửa lỗi Relay chưa produce vào Kafka. Retention dài hơn giảm nguy cơ mất offset nhưng không tăng tốc xử lý; backlog/throughput và lỗi trước Kafka phải được phân biệt. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Verify tham chiếu

```bash
docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --topic ingest-events --describe
docker inspect sentry-self-hosted-events-consumer-1 --format '{{json .Config.Cmd}}'
docker compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ingest-consumer --describe
```

Các lệnh nguồn dùng để xác nhận partition/command/lag; kết hợp snapshot tài nguyên, log và dữ liệu mới đến UI trước kết luận ingest ổn định. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Liên quan: [[Chẩn đoán pipeline ingest Sentry]], [[Kafka OffsetOutOfRange trong Sentry]], [[Relay buffer đầy và HTTP 503]].
