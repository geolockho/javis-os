---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["ingest-consumer", "OffsetOutOfRange", "Kafka reset offsets", "Kafka retention"]
source: ["[[sources/readme/sentry-self-hosted-ingest-troubleshooting]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Kafka OffsetOutOfRange trong Sentry

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận case Sentry đã xử lý được và `closed`. Các sự cố/503/drop và thông số bên dưới là lịch sử trong nguồn, không tiếp tục coi case này đang mở. Ngày đo cũ và chi tiết biện pháp sửa cuối cùng chưa được cung cấp; lần cập nhật này không kiểm tra live. [[sources/readme/open-questions-answers-2026-10-07]]

OffsetOutOfRange trong case Sentry là committed offset trỏ tới message broker không còn giữ, làm events-consumer crash và group rebalancing. Trang này là runbook/case từ nguồn, không xác nhận lỗi đang xảy ra hoặc cho phép tự reset live. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Quy ước kiểm tra retention theo từng lần lỗi

Người dùng yêu cầu linh hoạt theo mỗi lần check lỗi. Khi được giao kiểm tra mới, đọc config retention/broker/topic/partition thực tế lúc đó và xác định phạm vi đơn vị trước tính capacity; không dùng cố định 500 MB hoặc 12 giờ từ case cũ. Đây là quy trình kiểm tra được chốt, không xác nhận giá trị mới. [[sources/readme/open-questions-answers-2026-10-07]]

## Bằng chứng và phạm vi

Group ingest-consumer trong nguồn có events-consumer/ingest-events, transactions-consumer/ingest-transactions và attachments-consumer/ingest-attachments. Events mất assignment trong khi transactions vẫn có member; cần kiểm tra group, member, state và container restart/OOM. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Ví dụ committed 9.935.763 < earliest 10.181.165 chỉ minh họa offset đã bị retention xóa. Nguồn ghi retention.hours=12, retention.bytes=500741824, segment.bytes=67108864, max.message.bytes=50000000 tại lúc khảo sát; đây không phải cấu hình live. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Nguồn diễn giải retention.bytes là khoảng 500 MB "cho topic"; đơn vị/phạm vi theo topic hay partition cần xác minh trước khi tính tổng dung lượng, đặc biệt sau tăng lên 4 partition. Không lấy con số này thành capacity chắc chắn. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Lệnh chẩn đoán tham chiếu: [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

```bash
docker compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ingest-consumer --describe
docker compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ingest-consumer --describe --members --verbose
docker compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ingest-consumer --describe --state
docker compose exec -T kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic ingest-events --time -2
```

## Hai lựa chọn reset (thao tác can thiệp)

Nguồn yêu cầu dừng tất cả member cùng group, đợi group Empty/Dead và members=0 trước reset. Không chỉ dừng events-consumer khi transactions/attachments vẫn active. Thời gian sleep 45 giây trong mẫu không thay việc kiểm tra state. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

- **Earliest:** xử lý message còn được giữ; không khôi phục dữ liệu đã bị xóa. Nguồn cảnh báo cleanup có thể tiếp tục khiến earliest vừa chọn lại không còn hợp lệ trước khi consumer nhận partition. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- **Latest:** bỏ backlog còn tồn của ingest-events để ưu tiên realtime; chỉ khi chấp nhận phần bị bỏ và hiểu tác động. Case ghi đã dùng latest, không suy rằng được phép áp dụng cho mọi lần lỗi. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Mẫu dry-run earliest theo nguồn, trước quyết định thực thi: [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

```bash
docker compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ingest-consumer --topic ingest-events --reset-offsets --to-earliest --dry-run
```

Nguồn yêu cầu reset riêng topic ingest-events, không toàn group để tránh thay offset transactions/attachments. Khởi động lại cả consumer, so offset hai lần cách nhau khoảng 30 giây, kiểm tra assignment đủ partition, CURRENT-OFFSET tiến, lag thấp/giảm, group Stable và hết lỗi/restart. Lag 0 ngay sau latest chỉ là expected reset, chưa chứng minh data flow hồi phục. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Liên quan: [[Chẩn đoán pipeline ingest Sentry]], [[Tăng throughput consumer Sentry]], [[Relay buffer đầy và HTTP 503]].
