---
type: source
source_kind: own-note
status: processed
created: 2026-10-07
processed_at: 2026-10-07
wiki_links: ["[[wiki/devops/Chẩn đoán pipeline ingest Sentry]]", "[[wiki/devops/Kafka OffsetOutOfRange trong Sentry]]", "[[wiki/devops/Tăng throughput consumer Sentry]]", "[[wiki/devops/Relay buffer đầy và HTTP 503]]"]
url: null
original_path: "D:\\private01\\readme\\sentry-self-hosted-ingest-troubleshooting.md"
original_sha256: 782d6d5c2a94d426002dd9885d6c65ee17c67ca4b2aeab81e945043c57be7c07
---

# Sentry Self-Hosted 24.1.0 – Tổng hợp sự cố ingest, Kafka lag và Relay 503

## 1. Mục tiêu xử lý

Hệ thống Sentry self-hosted gặp các vấn đề:

- Event/log lên Sentry chậm.
- `events-consumer` có lúc restart.
- Kafka consumer lag tăng mạnh.
- Kafka báo `OffsetOutOfRange`.
- Sau khi tăng tốc consumer, có thời điểm Kafka lag về `0` nhưng không có offset mới.
- Nginx nhận request `/api/<project_id>/envelope/` nhưng trả `503`.
- Relay báo:
  - `envelope buffer capacity exceeded`
  - `dropped envelope: internal error`

Mục tiêu chính là:

1. Làm `events-consumer` xử lý nhanh hơn.
2. Giảm Kafka consumer lag.
3. Ngăn Relay trả `503`.
4. Ngăn event bị drop trước khi ghi vào Kafka.
5. Xác định đúng bottleneck thay vì chỉ tăng tài nguyên hoặc tăng retention.

---

## 2. Kiến trúc ingest liên quan

Luồng event chính:

```text
Sentry SDK
    |
    v
Nginx
    |
    v
Relay
    |
    v
Kafka topic: ingest-events
    |
    v
events-consumer
    |
    v
Snuba / ClickHouse / Postgres / các thành phần xử lý phía sau
    |
    v
Sentry UI
```

Ý nghĩa từng lớp:

- **Nginx**: nhận HTTP request từ SDK.
- **Relay**: validate, normalize, process envelope và ghi message vào Kafka.
- **Kafka**: lưu event tạm thời theo topic và partition.
- **events-consumer**: đọc `ingest-events` và đưa event sang các bước xử lý tiếp theo.
- **Worker**: xử lý background jobs của Sentry, dùng rất nhiều CPU trong hệ thống hiện tại.

---

## 3. Trạng thái ban đầu

### 3.1 Host

Trước khi tăng tài nguyên, host có tình trạng:

- Khoảng `16 CPU`.
- Load average khoảng:
  - `23.75`
  - `23.35`
  - `22.36`
- RAM gần đầy.
- Swap sử dụng cao.
- Docker container `worker` tiêu thụ CPU rất lớn.
- `events-consumer` có lúc dùng gần `100% CPU`.

Sau đó host đã được tăng tài nguyên.

Tại thời điểm kiểm tra sau này:

- Memory limit nhìn từ container khoảng `31.39 GiB`.
- Relay dùng rất ít RAM và CPU.
- Worker vẫn dùng CPU rất lớn.

---

## 4. Lỗi Kafka OffsetOutOfRange

### 4.1 Hiện tượng

`events-consumer` log lỗi:

```text
OffsetOutOfRange
requested offset not available
```

Nguyên nhân:

- Consumer group lưu offset cũ.
- Kafka retention đã xóa segment chứa offset đó.
- Consumer cố đọc offset không còn tồn tại.

### 4.2 Kafka retention hiện tại

Topic `ingest-events` có config:

```text
segment.bytes=67108864
max.message.bytes=50000000
retention.bytes=500741824
```

Trong file cấu hình Sentry có:

```text
KAFKA_LOG_RETENTION_HOURS=12
KAFKA_LOG_RETENTION_BYTES=500741824
```

Điều này có nghĩa Kafka chỉ giữ khoảng `500 MB` cho topic theo cấu hình retention bytes. Khi traffic lớn, dữ liệu cũ có thể bị xóa rất nhanh.

### 4.3 Cách đã xử lý

Dừng các consumer trong group:

- `events-consumer`
- `transactions-consumer`
- `attachments-consumer`

Đợi consumer group về trạng thái `Empty`, sau đó reset offset.

Cuối cùng đã reset `ingest-events` về `latest`, bỏ qua backlog cũ để consumer tiếp tục chạy.

Sau khi reset:

- Consumer không còn bị kẹt ở offset đã bị xóa.
- `events-consumer` hoạt động lại.
- Các event cũ bị bỏ qua theo thiết kế của việc reset `latest`.

---

## 5. Bottleneck ban đầu của events-consumer

### 5.1 Topic chỉ có một partition

Ban đầu:

```text
Topic: ingest-events
PartitionCount: 1
ReplicationFactor: 1
```

Với một partition, khả năng parallel đọc Kafka bị giới hạn.

### 5.2 Cấu hình events-consumer ban đầu

```yaml
events-consumer:
  <<: *sentry_defaults
  command: run consumer ingest-events --consumer-group ingest-consumer
```

Consumer hỗ trợ các option:

```text
--processes INTEGER
--input-block-size INTEGER
--output-block-size INTEGER
--max-batch-size INTEGER
--max-batch-time-ms INTEGER
```

---

## 6. Thay đổi đã thực hiện để tăng throughput

### 6.1 Tăng partition từ 1 lên 4

Lệnh:

```bash
docker exec sentry-self-hosted-kafka-1 \
  kafka-topics \
  --bootstrap-server localhost:9092 \
  --alter \
  --topic ingest-events \
  --partitions 4
```

Verify:

```bash
docker exec sentry-self-hosted-kafka-1 \
  kafka-topics \
  --bootstrap-server localhost:9092 \
  --topic ingest-events \
  --describe
```

Kết quả:

```text
Topic: ingest-events
PartitionCount: 4
ReplicationFactor: 1
```

Partition hiện tại:

```text
Partition 0
Partition 1
Partition 2
Partition 3
```

### Cảnh báo quan trọng

Kafka cho phép tăng partition nhưng không giảm partition trực tiếp.

Việc tăng partition có thể ảnh hưởng đến message ordering theo key. Với Sentry hiện tại hệ thống vẫn hoạt động, nhưng không nên tiếp tục tăng tùy tiện mà chưa đánh giá kỹ.

---

### 6.2 Tăng events-consumer lên 4 processes

Cấu hình đã sửa:

```yaml
events-consumer:
  <<: *sentry_defaults
  command: run consumer ingest-events --consumer-group ingest-consumer -- --processes 4
```

Lưu ý:

- Option đúng là `--processes`, số nhiều.
- Cú pháp phải có `--` trước option riêng của subcommand.

Recreate:

```bash
cd ~/self-hosted

docker compose up -d --force-recreate events-consumer
```

Verify command:

```bash
docker inspect sentry-self-hosted-events-consumer-1 \
  --format '{{json .Config.Cmd}}'
```

Kết quả:

```json
["run","consumer","ingest-events","--consumer-group","ingest-consumer","--","--processes","4"]
```

---

## 7. Kết quả sau khi tăng partition và processes

Consumer group đọc đủ 4 partition:

```text
ingest-events partition 0
ingest-events partition 1
ingest-events partition 2
ingest-events partition 3
```

Lag ban đầu sau thay đổi:

```text
Partition 0: 1552
Partition 1: 92
Partition 2: 80
Partition 3: 89
```

Sau đó giảm còn khoảng:

```text
Partition 0: 33
Partition 1: 34
Partition 2: 33
Partition 3: 44
```

Tổng lag giảm từ khoảng:

```text
1813
```

xuống còn khoảng:

```text
144
```

Có thời điểm toàn bộ lag về:

```text
0
```

Kết luận:

- Thay đổi 4 partition + 4 processes giúp consumer xử lý backlog tốt hơn.
- Consumer đã có thể bắt kịp Kafka trong một số thời điểm.
- Tuy nhiên việc này không giải quyết bottleneck nằm trước Kafka.

---

## 8. Tài nguyên events-consumer và worker

Kết quả Docker stats:

```text
events-consumer:
CPU: 65.61%
RAM: 676.8 MiB
PIDS: 29

worker:
CPU: 1474.08%
RAM: 3.204 GiB
PIDS: 421
```

Nhận định:

- `events-consumer` không còn saturate một core như trước.
- `worker` dùng khoảng `14.7 CPU cores`.
- Worker là container tranh CPU lớn nhất.
- Worker có thể ảnh hưởng toàn hệ thống nếu host không đủ CPU.
- Tuy nhiên tại thời điểm Relay lỗi, Relay chỉ dùng khoảng:
  - CPU `10.43%`
  - RAM `143.9 MiB`
- Do đó lỗi Relay buffer đầy không phải do container Relay hết CPU hoặc RAM.

---

## 9. Hiện tượng Kafka lag về 0 nhưng không có offset mới

Kết quả consumer group:

```text
CURRENT-OFFSET = LOG-END-OFFSET
LAG = 0
```

Các offset đứng yên qua nhiều lần kiểm tra.

Điều này không có nghĩa consumer lỗi.

Nó có nghĩa:

```text
Không có message mới được ghi vào topic ingest-events
```

Luồng cần kiểm tra lúc này là:

```text
SDK -> Nginx -> Relay -> Kafka
```

---

## 10. Phát hiện Nginx trả 503

Log Nginx:

```text
POST /api/2/envelope/ HTTP/1.1 503
POST /api/11/envelope/ HTTP/1.1 503
```

Có nhiều request từ:

- Flutter iOS SDK
- Flutter Android SDK
- Backend/internal source

Kết luận:

- Request vẫn đến Sentry.
- Nginx nhận request.
- Upstream Relay trả lỗi.
- Event chưa được ghi vào Kafka.
- Vì vậy `LOG-END-OFFSET` đứng yên.

---

## 11. Phát hiện Relay buffer đầy

Relay log:

```text
failed to queue envelope
envelope buffer capacity exceeded
dropped envelope: internal error
```

Ý nghĩa:

- Relay nhận envelope.
- Queue nội bộ Relay đã đầy.
- Relay từ chối envelope mới.
- Nginx trả `503`.
- Event bị drop trước Kafka.
- Event bị drop sẽ không xuất hiện trong Sentry UI.
- Việc tăng tốc `events-consumer` không trực tiếp sửa được lỗi này vì bottleneck nằm trước Kafka.

---

## 12. Cấu hình Relay ban đầu

File:

```text
~/self-hosted/relay/config.yml
```

Nội dung ban đầu:

```yaml
relay:
  upstream: "http://web:9000/"
  host: 0.0.0.0
  port: 3000

logging:
  level: WARN

processing:
  enabled: true
  kafka_config:
    - {name: "bootstrap.servers", value: "kafka:9092"}
    - {name: "message.max.bytes", value: 50000000}
  redis: redis://redis:6379
  geoip_path: "/geoip/GeoLite2-City.mmdb"
```

Relay version:

```text
relay 24.1.0
```

---

## 13. Relay effective config

Lệnh:

```bash
docker exec relay relay config show
```

Phát hiện mặc định:

```yaml
cache:
  envelope_expiry: 600
  envelope_buffer_size: 1000
  batch_interval: 100
  batch_size: 500
```

Giới hạn mặc định:

```text
envelope_buffer_size = 1000
```

Đây là một nguyên nhân trực tiếp khiến traffic burst nhanh chóng làm đầy queue.

---

## 14. Thay đổi Relay buffer

Đã thêm vào cuối file:

```yaml
cache:
  envelope_buffer_size: 10000
```

File hiện tại:

```yaml
relay:
  upstream: "http://web:9000/"
  host: 0.0.0.0
  port: 3000

logging:
  level: WARN

processing:
  enabled: true
  kafka_config:
    - {name: "bootstrap.servers", value: "kafka:9092"}
    - {name: "message.max.bytes", value: 50000000}
  redis: redis://redis:6379
  geoip_path: "/geoip/GeoLite2-City.mmdb"

cache:
  envelope_buffer_size: 10000
```

Recreate Relay:

```bash
cd ~/self-hosted

docker compose up -d --force-recreate relay
```

Verify:

```bash
docker exec relay relay config show 2>/dev/null \
  | grep -n -B2 -A2 'envelope_buffer_size'
```

Kết quả:

```text
envelope_buffer_size: 10000
```

---

## 15. Kết quả sau khi tăng Relay buffer

Relay vẫn báo:

```text
envelope buffer capacity exceeded
```

Ngay cả khi buffer đã tăng từ:

```text
1000 -> 10000
```

Kết luận quan trọng:

- Tăng buffer chỉ giúp hấp thụ burst lâu hơn.
- Buffer vẫn đầy chứng minh tốc độ input lớn hơn tốc độ Relay xử lý/xả.
- Không nên tiếp tục tăng buffer vô hạn.
- Nếu mỗi envelope trung bình khoảng `50–70 KB`, queue 10.000 envelope có thể chiếm hàng trăm MB, thậm chí nhiều hơn do overhead.
- Tăng buffer không làm tăng throughput.
- Nút thắt thật sự nằm ở khả năng xử lý của Relay hoặc các dependency mà Relay gọi tới.

---

## 16. Relay processing config hiện tại

Effective config:

```yaml
processing:
  enabled: true
  geoip_path: /geoip/GeoLite2-City.mmdb
  max_secs_in_future: 60
  max_secs_in_past: 2592000
  max_session_secs_in_past: 432000

  kafka_config:
    - name: bootstrap.servers
      value: kafka:9092
    - name: message.max.bytes
      value: "50000000"

  secondary_kafka_configs: {}

  topics:
    events: ingest-events
    attachments: ingest-attachments
    transactions: ingest-transactions
    outcomes: outcomes
    sessions: ingest-sessions
    metrics: ingest-metrics
    metrics_generic: ingest-performance-metrics
    profiles: profiles
    replay_events: ingest-replay-events
    replay_recordings: ingest-replay-recordings
    monitors: ingest-monitors
    spans: ingest-spans

  redis: redis://redis:6379
  attachment_chunk_size: 1MiB
  projectconfig_cache_prefix: relayconfig
  max_rate_limit: 300
```

Không thấy tham số concurrency/worker rõ ràng trong config version 24.1.0.

---

## 17. Những gì đã xác định chắc chắn

### Đã xử lý

- Kafka `OffsetOutOfRange`.
- Consumer group bị kẹt offset cũ.
- Topic `ingest-events` đã tăng lên 4 partition.
- `events-consumer` đã chạy với `--processes 4`.
- Consumer có thể bắt kịp backlog và đưa lag về 0.
- Relay buffer đã tăng từ 1.000 lên 10.000.

### Chưa xử lý xong

- Relay vẫn đầy buffer.
- Nginx vẫn có thể trả `503`.
- Envelope vẫn bị drop.
- Chưa xác định throughput đầu vào chính xác.
- Chưa xác định bottleneck bên trong Relay là:
  - processing CPU/thread
  - Redis
  - Kafka producer flush
  - project config fetch
  - downstream web/API
  - disk/network
  - traffic burst quá lớn
  - một hoặc nhiều project gửi lỗi lặp với tốc độ bất thường

---

## 18. Lưu ý về các nhận định trước đó

### Không nên kết luận rằng chỉ tăng partition là đủ

Tăng partition + processes giúp phía consumer, nhưng không giúp khi Relay chưa ghi được message vào Kafka.

### Không nên chỉ tăng Kafka retention

Kafka retention dài hơn giúp tránh `OffsetOutOfRange`, nhưng không làm hệ thống xử lý nhanh hơn.

### Không nên chỉ tăng Relay buffer

Buffer lớn hơn không tăng throughput.

Khi input rate > processing rate:

```text
queue sẽ luôn đầy
```

### Không nên reset Kafka offset liên tục

Reset offset có thể làm mất event chưa xử lý.

Chỉ reset khi:

- Đã xác định offset không còn tồn tại.
- Chấp nhận bỏ backlog.
- Consumer group đã dừng.
- Có backup hoặc hiểu rõ tác động.

---

## 19. Lệnh kiểm tra nhanh cho lần sau

### 19.1 Kiểm tra toàn bộ container chính

```bash
docker compose ps
```

### 19.2 Kiểm tra CPU/RAM

```bash
docker stats --no-stream \
  relay \
  sentry-self-hosted-events-consumer-1 \
  sentry-self-hosted-worker-1 \
  sentry-self-hosted-kafka-1 \
  sentry-self-hosted-redis-1
```

### 19.3 Kiểm tra host CPU/load

```bash
nproc
uptime
free -h
```

### 19.4 Kiểm tra consumer lag

```bash
docker exec sentry-self-hosted-kafka-1 \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe
```

### 19.5 Kiểm tra topic partition

```bash
docker exec sentry-self-hosted-kafka-1 \
  kafka-topics \
  --bootstrap-server localhost:9092 \
  --topic ingest-events \
  --describe
```

### 19.6 Kiểm tra Nginx envelope status

```bash
docker logs --since 5m sentry-self-hosted-nginx-1 2>&1 \
  | grep 'POST /api/.*/envelope/' \
  | tail -n 100
```

### 19.7 Đếm HTTP status trong 1 phút

```bash
docker logs --since 1m sentry-self-hosted-nginx-1 2>&1 \
  | awk '
    /POST \/api\/[0-9]+\/envelope\// {
      total++
      status[$9]++
    }
    END {
      print "TOTAL=" total
      for (s in status) print "STATUS_" s "=" status[s]
    }
  '
```

### 19.8 Kiểm tra Relay buffer errors

```bash
docker logs --since 5m relay 2>&1 \
  | grep -E 'envelope buffer capacity exceeded|dropped envelope' \
  | tail -n 100
```

### 19.9 Kiểm tra Relay config hiệu lực

```bash
docker exec relay relay config show
```

### 19.10 Kiểm tra Relay version

```bash
docker exec relay relay --version
```

### 19.11 Kiểm tra command events-consumer

```bash
docker inspect sentry-self-hosted-events-consumer-1 \
  --format '{{json .Config.Cmd}}'
```

Expected:

```json
["run","consumer","ingest-events","--consumer-group","ingest-consumer","--","--processes","4"]
```

---

## 20. Bước tiếp theo nên làm ở lần xử lý sau

### Bước 1: đo traffic envelope thật

Chạy trong thời điểm hệ thống lỗi:

```bash
docker logs --since 1m sentry-self-hosted-nginx-1 2>&1 \
  | awk '
    /POST \/api\/[0-9]+\/envelope\// {
      total++
      status[$9]++
    }
    END {
      print "TOTAL=" total
      for (s in status) print "STATUS_" s "=" status[s]
    }
  '
```

Cần biết:

- Bao nhiêu request/phút.
- Bao nhiêu `200`.
- Bao nhiêu `503`.

### Bước 2: tìm project gây traffic lớn

Có thể nhóm theo project ID trong URL:

```bash
docker logs --since 1m sentry-self-hosted-nginx-1 2>&1 \
  | grep 'POST /api/.*/envelope/' \
  | sed -n 's#.*POST /api/\([0-9]\+\)/envelope/.*#\1#p' \
  | sort \
  | uniq -c \
  | sort -nr
```

Mục tiêu:

- Xác định project nào gửi nhiều envelope nhất.
- Kiểm tra có application bị error loop hay không.

### Bước 3: đo size envelope theo project

Nginx access log hiện có response size nhưng chưa chắc có request body size.

Cần kiểm tra format log Nginx hoặc Relay metric để biết:

- Envelope trung bình bao nhiêu KB.
- Một project có gửi payload 50–80 KB liên tục hay không.

### Bước 4: kiểm tra Relay metrics

Tìm endpoint metrics hoặc stats của Relay.

Có thể thử kiểm tra port/endpoint:

```bash
docker exec relay sh -c 'wget -qO- http://127.0.0.1:3000/api/relay/healthcheck/ || true'
```

Sau đó tìm metrics config trong Relay 24.1.0.

### Bước 5: kiểm tra Kafka producer từ Relay

Relay log level hiện là:

```yaml
logging:
  level: WARN
```

Có thể tạm tăng lên:

```yaml
logging:
  level: INFO
```

Hoặc debug trong thời gian ngắn để xem:

- Kafka producer latency.
- Batch flush.
- Queue time.
- Retry.
- Timeout.
- Redis latency.
- Project config fetch.

Không nên để DEBUG lâu vì log sẽ rất lớn.

### Bước 6: kiểm tra Redis latency

```bash
docker exec sentry-self-hosted-redis-1 redis-cli --latency
```

Hoặc:

```bash
docker exec sentry-self-hosted-redis-1 redis-cli INFO stats
```

Cần xem:

- blocked_clients
- rejected_connections
- instantaneous_ops_per_sec
- evicted_keys
- keyspace_hits
- keyspace_misses

### Bước 7: kiểm tra Kafka producer/broker health

```bash
docker logs --since 10m sentry-self-hosted-kafka-1 2>&1 \
  | tail -n 200
```

Kiểm tra:

- Under replicated partitions.
- Disk errors.
- Request queue delay.
- Message too large.
- Network thread saturation.

### Bước 8: kiểm tra disk I/O host

```bash
iostat -xz 1 10
```

Nếu chưa có:

```bash
apt-get update
apt-get install -y sysstat
```

Quan sát:

- `%util`
- `await`
- `r_await`
- `w_await`
- queue depth

### Bước 9: cân nhắc scale Relay

Relay hiện chỉ có một container:

```text
relay
```

Nếu throughput đầu vào vượt khả năng một Relay, cần cân nhắc:

- Chạy nhiều Relay instance.
- Đặt Nginx load balance tới nhiều Relay.
- Mỗi Relay có processing enabled.
- Kiểm tra tính tương thích với compose version hiện tại.
- Đảm bảo tất cả Relay dùng cùng Kafka, Redis, upstream và config.

Không nên scale ngay khi chưa đo request rate và chưa kiểm tra Relay 24.1.0 support pattern.

### Bước 10: giảm dữ liệu không cần thiết từ SDK

Đây thường là cách hiệu quả nhất khi có error storm.

Kiểm tra:

- `sample_rate`
- `traces_sample_rate`
- `profiles_sample_rate`
- session tracking
- breadcrumbs
- attachments
- duplicate error
- retry loop
- release bị crash hàng loạt

Có thể giảm tạm:

```text
traces_sample_rate
profiles_sample_rate
send_default_pii
max_breadcrumbs
```

Hoặc dùng `before_send` để drop error không cần thiết.

---

## 21. Trạng thái cấu hình hiện tại cần giữ

### Kafka

```text
ingest-events partitions: 4
```

### events-consumer

```yaml
events-consumer:
  <<: *sentry_defaults
  command: run consumer ingest-events --consumer-group ingest-consumer -- --processes 4
```

### Relay

```yaml
cache:
  envelope_buffer_size: 10000
```

### Kafka retention

```text
KAFKA_LOG_RETENTION_HOURS=12
KAFKA_LOG_RETENTION_BYTES=500741824
```

---

## 22. Rủi ro đang tồn tại

1. **Event loss**
   - Relay đang drop envelope khi buffer đầy.
   - SDK có thể retry một phần, nhưng không nên giả định toàn bộ event sẽ được gửi lại.

2. **Kafka data loss do retention thấp**
   - Backlog lớn có thể bị Kafka xóa trước khi consumer đọc.

3. **Worker CPU cao**
   - Worker dùng gần 15 CPU cores.
   - Có thể gây contention cho Kafka, Redis, Relay và ClickHouse.

4. **Single Kafka broker**
   - Replication factor hiện là `1`.
   - Kafka broker lỗi có thể mất availability hoặc mất dữ liệu.

5. **Partition increase không rollback**
   - Topic đã tăng lên 4 partition.
   - Không giảm trực tiếp lại được.

6. **Relay buffer chỉ là giải pháp hấp thụ burst**
   - Không phải giải pháp scale throughput lâu dài.

---

## 23. Kết luận ngắn

Hệ thống đã xử lý được bottleneck của `events-consumer` bằng:

```text
1 partition -> 4 partitions
1 process -> 4 processes
```

Kafka lag có thể giảm về `0`.

Tuy nhiên sự cố chính hiện tại chuyển sang phía trước Kafka:

```text
SDK -> Nginx -> Relay
```

Nginx trả:

```text
503
```

Relay báo:

```text
envelope buffer capacity exceeded
```

Dù đã tăng:

```text
envelope_buffer_size: 1000 -> 10000
```

buffer vẫn đầy.

Điều này chứng minh:

```text
Tốc độ envelope vào Relay lớn hơn tốc độ Relay xử lý/xả.
```

Hướng xử lý tiếp theo không phải tiếp tục tăng buffer, mà là:

1. Đo request rate.
2. Xác định project gây burst.
3. Kiểm tra Redis/Kafka/disk latency.
4. Kiểm tra error storm từ SDK.
5. Đánh giá scale nhiều Relay.
6. Giảm event/tracing/profile không cần thiết.






# Xử lý lỗi Kafka `OffsetOutOfRange` trên Sentry Self-Hosted

## 1. Mô tả sự cố

Trong Sentry Self-Hosted, consumer group `ingest-consumer` liên tục rơi vào trạng thái `rebalancing`.

Các biểu hiện chính:

* `transactions-consumer` vẫn chạy và giữ partition `ingest-transactions`.
* `attachments-consumer` vẫn tham gia consumer group.
* `events-consumer` khởi động nhưng không giữ được các partition của topic `ingest-events`.
* Offset của `ingest-events` có thể tăng một lần rồi dừng.
* Container `events-consumer` liên tục restart.
* Lag của topic `ingest-events` tiếp tục tăng.
* Log xuất hiện lỗi:

```text
arroyo.errors.OffsetOutOfRange:
KafkaError{
  code=_AUTO_OFFSET_RESET,
  val=-140,
  str="fetch failed due to requested offset not available on the broker:
  Broker: Offset out of range"
}
```

Thông báo quan trọng:

```text
requested offset not available on the broker
```

---

## 2. Nguyên nhân

Consumer group `ingest-consumer` đang lưu một `CURRENT-OFFSET` không còn tồn tại trên Kafka broker.

Tình huống thường xảy ra khi:

* Kafka đã xóa các message cũ theo retention policy.
* Consumer bị dừng trong thời gian dài.
* Kafka disk đầy hoặc Kafka bị gián đoạn.
* Consumer lag quá lâu so với thời gian retention.
* Dữ liệu Kafka đã bị cleanup nhưng committed offset của consumer group vẫn trỏ vào vùng dữ liệu cũ.
* Consumer group được khôi phục nhưng offset không còn hợp lệ.

Ví dụ:

```text
CURRENT-OFFSET: 9,935,763
EARLIEST-OFFSET: 10,181,165
```

Trong trường hợp này, consumer yêu cầu đọc từ offset `9,935,763`, nhưng Kafka chỉ còn dữ liệu bắt đầu từ offset `10,181,165`.

Kafka trả về:

```text
OffsetOutOfRange
```

`events-consumer` bị crash, rời khỏi consumer group, sau đó được Docker restart. Việc này làm consumer group liên tục:

```text
Stable -> PreparingRebalance -> Rebalancing -> Stable
```

Do đó có hiện tượng:

* `transactions-consumer` vẫn chạy.
* `events-consumer` không giữ được partition `ingest-events`.
* Consumer group liên tục rebalancing.

---

# 3. Các service liên quan

Consumer group:

```text
ingest-consumer
```

Các service dùng chung group:

```text
events-consumer
transactions-consumer
attachments-consumer
```

Các topic tương ứng:

```text
events-consumer       -> ingest-events
transactions-consumer -> ingest-transactions
attachments-consumer  -> ingest-attachments
```

Do các service dùng chung consumer group, muốn reset offset thì phải dừng toàn bộ member của group trước.

---

# 4. Quy trình kiểm tra

## 4.1. Kiểm tra trạng thái container

```bash
cd ~/self-hosted

docker compose ps \
  events-consumer \
  attachments-consumer \
  transactions-consumer
```

Kiểm tra các dấu hiệu:

* Container có liên tục restart không.
* `events-consumer` có thời gian uptime rất ngắn không.
* Trạng thái có phải `Up` ổn định không.

Kiểm tra chi tiết container:

```bash
docker inspect sentry-self-hosted-events-consumer-1 \
  --format '
Status={{.State.Status}}
Running={{.State.Running}}
Restarting={{.State.Restarting}}
OOMKilled={{.State.OOMKilled}}
ExitCode={{.State.ExitCode}}
RestartCount={{.RestartCount}}
StartedAt={{.State.StartedAt}}
FinishedAt={{.State.FinishedAt}}
'
```

---

## 4.2. Kiểm tra log `events-consumer`

```bash
docker compose logs \
  --since=10m \
  --tail=300 \
  events-consumer
```

Lọc lỗi liên quan:

```bash
docker compose logs --since=10m events-consumer |
grep -Ei \
'OffsetOutOfRange|requested offset not available|error|fatal|exception'
```

Lỗi xác nhận sự cố:

```text
arroyo.errors.OffsetOutOfRange
```

```text
fetch failed due to requested offset not available on the broker
```

---

## 4.3. Kiểm tra consumer group

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe
```

Output cần chú ý:

```text
TOPIC
PARTITION
CURRENT-OFFSET
LOG-END-OFFSET
LAG
CONSUMER-ID
HOST
```

Dấu hiệu bất thường:

* `CURRENT-OFFSET` đứng yên.
* `LOG-END-OFFSET` tiếp tục tăng.
* `LAG` tiếp tục tăng.
* `CONSUMER-ID` của `ingest-events` là `-`.
* `transactions-consumer` vẫn có consumer ID.
* Kafka hiển thị:

```text
Warning: Consumer group 'ingest-consumer' is rebalancing.
```

---

## 4.4. Kiểm tra member của consumer group

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe \
  --members \
  --verbose
```

Ví dụ:

```text
GROUP           CONSUMER-ID      HOST            ASSIGNMENT
ingest-consumer rdkafka-...      /172.18.0.39    ingest-transactions(0)
```

Dựa vào IP để xác định container đang giữ partition.

Liệt kê IP container:

```bash
docker inspect $(docker ps -q) \
  --format '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' |
sort
```

Ví dụ:

```text
/sentry-self-hosted-transactions-consumer-1 172.18.0.39
```

---

## 4.5. Kiểm tra trạng thái consumer group

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe \
  --state
```

Khi còn consumer chạy:

```text
STATE: Stable
MEMBERS: 1
```

Khi đã dừng toàn bộ consumer:

```text
Consumer group 'ingest-consumer' has no active members.

STATE: Empty
MEMBERS: 0
```

Chỉ reset offset khi group ở trạng thái:

```text
Empty
```

hoặc:

```text
Dead
```

---

## 4.6. Kiểm tra earliest offset còn tồn tại

```bash
docker compose exec -T kafka \
  kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic ingest-events \
  --time -2
```

Ví dụ:

```text
ingest-events:0:10189563
ingest-events:1:2876184
ingest-events:2:2876123
ingest-events:3:2880281
```

Ý nghĩa:

```text
topic:partition:earliest-offset
```

Nếu committed offset của consumer group nhỏ hơn các giá trị này thì offset cũ đã bị Kafka xóa.

---

# 5. Quy trình xử lý

## 5.1. Dừng toàn bộ consumer dùng chung group

```bash
cd ~/self-hosted

docker compose stop \
  events-consumer \
  attachments-consumer \
  transactions-consumer
```

Chờ consumer group hoàn tất rebalance và loại bỏ toàn bộ member:

```bash
sleep 45
```

Kiểm tra:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe \
  --state
```

Kết quả yêu cầu:

```text
Consumer group 'ingest-consumer' has no active members.

STATE: Empty
MEMBERS: 0
```

---

## 5.2. Phương án 1: Reset về earliest còn tồn tại

Phương án này cố gắng xử lý toàn bộ message còn được Kafka lưu giữ.

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --topic ingest-events \
  --reset-offsets \
  --to-earliest \
  --dry-run
```

Thực hiện:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --topic ingest-events \
  --reset-offsets \
  --to-earliest \
  --execute
```

Kiểm tra:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe
```

### Lưu ý

Trong một số trường hợp, Kafka tiếp tục cleanup segment trong thời gian xử lý.

Offset vừa reset về earliest có thể lại trở thành offset không còn tồn tại trước khi consumer khởi động và nhận partition.

Khi đó `events-consumer` vẫn có thể tiếp tục báo:

```text
OffsetOutOfRange
```

Nếu tình trạng này lặp lại, chuyển sang phương án reset về latest.

---

## 5.3. Phương án 2: Reset về latest

Phương án này bỏ qua backlog hiện có của topic `ingest-events` và cho consumer đọc từ message mới nhất.

Chỉ reset riêng topic:

```text
ingest-events
```

Không reset toàn bộ consumer group, tránh ảnh hưởng đến:

```text
ingest-transactions
ingest-attachments
```

Thực hiện:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --topic ingest-events \
  --reset-offsets \
  --to-latest \
  --execute
```

Ví dụ output:

```text
GROUP             TOPIC          PARTITION  NEW-OFFSET
ingest-consumer   ingest-events  0          10207912
ingest-consumer   ingest-events  1          2893694
ingest-consumer   ingest-events  2          2893972
ingest-consumer   ingest-events  3          2897794
```

Kiểm tra:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe
```

Kết quả mong đợi:

```text
CURRENT-OFFSET gần bằng LOG-END-OFFSET
LAG bằng 0 hoặc rất nhỏ
```

Do producer vẫn tiếp tục ghi message trong khi consumer đang dừng, lag có thể tăng nhẹ sau khi reset. Đây là bình thường.

### Cảnh báo

Reset về latest sẽ bỏ qua toàn bộ message chưa xử lý hiện đang còn trong topic `ingest-events`.

Chỉ dùng khi:

* Backlog cũ không thể xử lý do offset invalid.
* Mục tiêu ưu tiên là khôi phục ingest realtime.
* Chấp nhận bỏ qua số message đang tồn đọng.
* Dữ liệu quan trọng đã được backup hoặc khôi phục bằng phương án khác.

---

## 5.4. Khởi động lại consumer

```bash
docker compose up -d \
  events-consumer \
  attachments-consumer \
  transactions-consumer
```

Chờ consumer join group:

```bash
sleep 30
```

---

# 6. Verify sau xử lý

## 6.1. Kiểm tra trạng thái container

```bash
docker compose ps \
  events-consumer \
  attachments-consumer \
  transactions-consumer
```

Kết quả mong đợi:

```text
events-consumer         Up
attachments-consumer    Up
transactions-consumer   Up
```

Container không được restart liên tục.

---

## 6.2. So sánh offset hai lần

```bash
for i in 1 2; do
  echo "===== SNAPSHOT $i: $(date '+%F %T') ====="

  docker compose exec -T kafka \
    kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group ingest-consumer \
    --describe

  [ "$i" -eq 1 ] && sleep 30
done
```

Ví dụ kết quả bình thường:

```text
SNAPSHOT 1

ingest-events partition 0
CURRENT-OFFSET: 10209094
LOG-END-OFFSET: 10209122
LAG: 28
```

```text
SNAPSHOT 2

ingest-events partition 0
CURRENT-OFFSET: 10209494
LOG-END-OFFSET: 10209512
LAG: 18
```

Điều kiện xác nhận xử lý thành công:

* `CURRENT-OFFSET` tăng giữa hai snapshot.
* `events-consumer` giữ đủ partition của `ingest-events`.
* `CONSUMER-ID` không còn là `-`.
* `LAG` thấp hoặc giảm.
* Consumer group không còn rebalancing liên tục.
* `transactions-consumer` vẫn xử lý bình thường.
* `attachments-consumer` tham gia consumer group bình thường.

Ví dụ assignment đúng:

```text
ingest-events       0   rdkafka-... /172.18.0.50
ingest-events       1   rdkafka-... /172.18.0.50
ingest-events       2   rdkafka-... /172.18.0.50
ingest-events       3   rdkafka-... /172.18.0.50
ingest-attachments  0   rdkafka-... /172.18.0.40
ingest-transactions 0   rdkafka-... /172.18.0.39
```

---

## 6.3. Kiểm tra không còn lỗi

```bash
docker compose logs --since=10m \
  events-consumer \
  attachments-consumer \
  transactions-consumer |
grep -Ei \
'OffsetOutOfRange|requested offset not available|error|fatal|exception'
```

Kết quả mong đợi:

```text
Không có output
```

Kiểm tra riêng `events-consumer`:

```bash
docker compose logs --since=10m events-consumer |
grep -Ei \
'OffsetOutOfRange|requested offset not available'
```

Không được còn xuất hiện:

```text
arroyo.errors.OffsetOutOfRange
```

---

## 6.4. Kiểm tra consumer group không còn rebalancing

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe \
  --state
```

Kết quả mong đợi:

```text
STATE: Stable
MEMBERS: 3
```

Số member có thể khác tùy cấu hình, nhưng group phải ở trạng thái:

```text
Stable
```

---

# 7. Checklist xử lý nhanh

## Check lỗi

```bash
docker compose logs --since=10m events-consumer |
grep -Ei \
'OffsetOutOfRange|requested offset not available|error|fatal|exception'
```

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe
```

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe \
  --members \
  --verbose
```

## Dừng consumer

```bash
docker compose stop \
  events-consumer \
  attachments-consumer \
  transactions-consumer
```

```bash
sleep 45
```

## Xác nhận group Empty

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --describe \
  --state
```

## Reset riêng `ingest-events`

Reset về earliest:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --topic ingest-events \
  --reset-offsets \
  --to-earliest \
  --execute
```

Hoặc reset về latest:

```bash
docker compose exec -T kafka \
  kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer \
  --topic ingest-events \
  --reset-offsets \
  --to-latest \
  --execute
```

## Start consumer

```bash
docker compose up -d \
  events-consumer \
  attachments-consumer \
  transactions-consumer
```

## Verify

```bash
for i in 1 2; do
  echo "===== SNAPSHOT $i: $(date '+%F %T') ====="

  docker compose exec -T kafka \
    kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group ingest-consumer \
    --describe

  [ "$i" -eq 1 ] && sleep 30
done
```

---

# 8. Kết luận

Lỗi xảy ra vì committed offset của `ingest-consumer` trỏ đến message đã bị Kafka xóa.

Điều này khiến:

```text
events-consumer
```

không thể đọc `ingest-events`, liên tục crash và làm consumer group rebalancing.

Quy trình xử lý đúng:

1. Xác định container và partition đang active.
2. Dừng toàn bộ service dùng chung consumer group.
3. Chờ group chuyển sang `Empty`.
4. Reset riêng topic bị lỗi.
5. Khởi động lại consumer.
6. So sánh offset qua hai snapshot.
7. Kiểm tra lag, assignment và log lỗi.

Sự cố được coi là xử lý xong khi:

* Consumer group ở trạng thái `Stable`.
* `events-consumer` giữ đủ partition `ingest-events`.
* `CURRENT-OFFSET` tiếp tục tăng.
* Lag duy trì ở mức thấp.
* Không còn lỗi `OffsetOutOfRange`.
* Container không restart liên tục.
