---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Submariner latency", "MTU MSS", "Gateway bottleneck", "HTTP TTFB"]
source: ["[[sources/readme/submarine multi-cluster]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Đo latency và MTU của Submariner

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận hiện chưa triển khai Submariner. Các thiết kế/checklist/ví dụ bên dưới là tài liệu tham khảo. Chỉ hỏi và kiểm chứng compatibility, route, ports, NAT, encryption, CIDR, Broker khi người dùng cần triển khai; không coi các mục này đã pass hoặc tự tạo việc theo dõi. [[sources/readme/open-questions-answers-2026-10-07]]

Chẩn đoán latency Submariner tách underlay, tunnel/gateway, CNI, service và application/dependency. Đây là phương pháp và ví dụ trong tài liệu 2026-08-12, không có benchmark live của các cluster người dùng. [[sources/readme/submarine multi-cluster]]

## Thang đo

Nguồn đề xuất Gateway -> Gateway RTT, Pod -> Pod RTT, subctl benchmark, simple HTTP service không DB/cache và real API. Tổng latency gồm local CNI, worker->gateway, encapsulation, inter-VPC RTT, decapsulation, remote CNI và application/DB/cache/external. [[sources/readme/submarine multi-cluster]]

Mẫu số minh họa 1,0 ms gateway, 1,6 ms Pod, 2,3 ms simple HTTP, 90 ms real API gợi ý bottleneck sau network; không phải kết quả đo thực tế. Mẫu curl connect 4 ms và TTFB 87 ms cũng chỉ hỗ trợ giả thuyết phần lớn delay sau connect, chưa đủ kết luận root cause. [[sources/readme/submarine multi-cluster]]

Lệnh baseline/HTTP theo nguồn: [[sources/readme/submarine multi-cluster]]

```bash
subctl benchmark latency --context cluster-a --tocontext cluster-b --verbose
subctl benchmark throughput --context cluster-a --tocontext cluster-b --verbose
curl -o /dev/null -s -w 'dns=%{time_namelookup} connect=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total}\n' http://user-api.backend.svc.clusterset.local:8080/health
```

Benchmark có workload test; cần chọn khung/phạm vi phù hợp lúc thực thi, chưa chạy trong ingest. [[sources/readme/submarine multi-cluster]]

## MTU và gateway

VXLAN overhead có thể dẫn fragmentation/drop/retransmission. Nguồn thử ping DF với payload 1400/1420/1440/1460/1472; nhỏ qua lớn fail thì nghi path MTU/MSS, không đặt MSS tùy ý chưa đo. [[sources/readme/submarine multi-cluster]]

Nguồn nêu annotation submariner.io/tcp-clamp-mss và restart Route Agent như cách can thiệp, phải đối chiếu version và đo path trước. Theo nguồn gateway active/passive không chia tải active-active; xem CPU/NIC, packet loss, RTT và failover ở gateway active. [[sources/readme/submarine multi-cluster]]

## Phân biệt đường truy cập

Gọi clusterset.local thường đi networking Pod/Service qua tunnel, không qua external FPT LB/Ingress. User -> LB -> Ingress là north-south riêng; đổ lỗi LB cho east-west cần bằng chứng path. [[sources/readme/submarine multi-cluster]]

Liên quan: [[Kiến trúc Submariner đa VPC]], [[Triển khai và khám lỗi Submariner]], [[Lighthouse và service discovery đa cluster]].
