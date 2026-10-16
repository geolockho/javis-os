---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Sentry Relay", "envelope_buffer_size", "Backpressure", "Envelope drops"]
source: ["[[sources/readme/sentry-self-hosted-ingest-troubleshooting]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Relay buffer đầy và HTTP 503

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận case Sentry đã xử lý được và `closed`. Các sự cố/503/drop và thông số bên dưới là lịch sử trong nguồn, không tiếp tục coi case này đang mở. Ngày đo cũ và chi tiết biện pháp sửa cuối cùng chưa được cung cấp; lần cập nhật này không kiểm tra live. [[sources/readme/open-questions-answers-2026-10-07]]

Relay buffer đầy là nhánh lỗi trước Kafka trong case Sentry self-hosted 24.1.0, có Nginx HTTP 503 và envelope bị drop. Đây là case lịch sử theo nguồn không có ngày đo; chưa biết tình trạng hiện tại của hệ thống. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Dấu hiệu và config hiệu lực

Nguồn ghi POST /api/2/envelope và /api/11/envelope trả 503, Relay log failed to queue envelope/envelope buffer capacity exceeded/dropped envelope. Kafka end offset đứng vì không nhận message mới; tăng consumer throughput không giải quyết nhánh này. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

File nguồn là `~/self-hosted/relay/config.yml`, Relay 24.1.0, upstream web:9000, processing enabled, Kafka kafka:9092, Redis redis:6379. `relay config show` cho thấy buffer mặc định 1.000, expiry 600, batch_interval 100, batch_size 500; nguồn không nêu đơn vị tất cả field, không tự suy đơn vị. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Thay đổi nguồn ghi đã làm: thêm cấu hình sau, recreate Relay và đọc effective config để xác nhận 10.000. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

```yaml
cache:
  envelope_buffer_size: 10000
```

## Kết quả chưa giải quyết xong ở thời điểm tài liệu cũ

Buffer 10.000 vẫn đầy và 503/drop còn xuất hiện. Nguồn suy input vượt khả năng xử lý/xả; đây là nhận định từ queue errors, throughput chưa được đo trực tiếp. Tăng buffer chỉ hấp thụ burst, không tăng processing rate. Ví dụ envelope 50-70 KB chỉ là giả định ước lượng RAM, không phải size đã đo. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Nguồn chưa xác định bottleneck cụ thể: processing/thread, Redis, Kafka producer flush, project config fetch, web/API, disk/network hay error storm. Effective config không lộ rõ concurrency/worker; không bịa parameter tuning cho version 24.1.0. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

## Runbook tham khảo cho lần lỗi mới

1. Đếm request/phút và status 200/503 cùng cửa sổ lỗi, nhóm project ID trong URL để tìm error loop/burst. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
2. Xác định request-body size qua log format/metric; response size của Nginx không chắc phản ánh envelope input. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
3. Kiểm tra metric/config Relay theo version; endpoint healthcheck được nguồn nêu để thử, chưa chứng minh là endpoint metrics. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
4. Kiểm tra Redis latency/blocked/rejected/eviction/cache, Kafka producer retry/flush/timeout và broker/disk I/O. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
5. Đánh giá scale nhiều Relay/Nginx LB sau đo input và compatibility compose; các instance phải thống nhất Kafka/Redis/upstream/config. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
6. Kiểm tra sampling, traces/profiles, breadcrumb/attachment, duplicate/retry loop; cân nhắc before_send khi có error storm. Đây là kế hoạch, chưa thực hiện trong nguồn. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Lệnh đọc tham chiếu; tên container từ case: [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

```bash
docker exec relay relay config show
docker exec relay relay --version
docker logs --since 5m relay
docker logs --since 1m sentry-self-hosted-nginx-1
docker exec sentry-self-hosted-redis-1 redis-cli INFO stats
docker logs --since 10m sentry-self-hosted-kafka-1
iostat -xz 1 10
```

Các rủi ro nguồn giữ rõ: envelope drop trước Kafka, backlog bị retention xóa, worker tranh CPU, single broker/replication 1. Không giả định SDK retry lại toàn bộ event đã drop. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

Liên quan: [[Chẩn đoán pipeline ingest Sentry]], [[Kafka OffsetOutOfRange trong Sentry]], [[Tăng throughput consumer Sentry]].
