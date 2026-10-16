---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["subctl join", "subctl diagnose", "Submariner deployment checklist"]
source: ["[[sources/readme/submarine multi-cluster]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Triển khai và khám lỗi Submariner

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận hiện chưa triển khai Submariner. Các thiết kế/checklist/ví dụ bên dưới là tài liệu tham khảo. Chỉ hỏi và kiểm chứng compatibility, route, ports, NAT, encryption, CIDR, Broker khi người dùng cần triển khai; không coi các mục này đã pass hoặc tự tạo việc theo dõi. [[sources/readme/open-questions-answers-2026-10-07]]

Trang này chưng cất quy trình Submariner hai cluster của tài liệu 2026-08-12. Cluster-a/b, IP/CIDR và flags đều là mẫu cần khớp phiên bản/môi trường; chưa triển khai hoặc verify live trong ingest. [[sources/readme/submarine multi-cluster]]

## Requirements trước deploy

Nguồn yêu cầu khảo sát CIDR/CNI/kube-proxy, private routes, NAT, UDP và API Broker. Tài liệu ghi "iptables supported, IPVS not supported" theo known issues thời điểm đó; cần xác minh compatibility version pin với FKE/Kubernetes/CNI, không coi là khẳng định cho mọi version hiện nay. Không dùng ignore-requirements để né check production. [[sources/readme/submarine multi-cluster]]

Phải xác nhận với FPT L3/UDP hai chiều, source IP/NAT, underlay có encrypt không và policy SG/firewall. Pin subctl/component đồng bộ version thay latest; install script trong nguồn chỉ là hướng dẫn, không thực thi khi ingest. [[sources/readme/submarine multi-cluster]]

## Triển khai (kế hoạch nguồn)

1. Label gateway candidate ở subnet hai chiều routable; production nguồn khuyên ít nhất hai mỗi cluster. [[sources/readme/submarine multi-cluster]]
2. Deploy Broker một nơi và giữ broker-info.subm để join. [[sources/readme/submarine multi-cluster]]
3. Join cả cluster chứa Broker lẫn remote; cluster ID unique, đúng Pod/Service CIDR và cable driver phù hợp. [[sources/readme/submarine multi-cluster]]
4. Kiểm tra operator/gateway/routeagent/Lighthouse, gateways/endpoints/connections. [[sources/readme/submarine multi-cluster]]
5. Diagnose firewall cả intra/inter, verify connectivity và service discovery, benchmark baseline rồi test gateway failover. [[sources/readme/submarine multi-cluster]]

Lệnh tham chiếu chẩn đoán/nghiệm thu; diagnose/verify/benchmark có thể tạo workload test, không mặc định chỉ đọc: [[sources/readme/submarine multi-cluster]]

```bash
subctl show all --context cluster-a
subctl show all --context cluster-b
subctl diagnose firewall intra-cluster --context cluster-a --verbose
subctl diagnose firewall inter-cluster --context cluster-a --remotecontext cluster-b --verbose
subctl verify --context cluster-a --tocontext cluster-b --only connectivity,service-discovery --verbose
```

## Phân nhánh lỗi

- Gateway không connected: xem connections/endpoints, route FPT, SG, gateway subnet, NAT, endpoint IP và port đúng driver. [[sources/readme/submarine multi-cluster]]
- Gateway gọi remote được nhưng worker không gọi được: kiểm tra internal UDP 4800, Route Agent, CNI/routing và rp_filter theo nguồn. [[sources/readme/submarine multi-cluster]]
- DNS clusterset.local lỗi: kiểm tra CoreDNS forwarding, Lighthouse, ServiceImport, EndpointSlice. [[sources/readme/submarine multi-cluster]]
- ServiceImport thiếu: kiểm tra ServiceExport nguồn, Broker path và Lighthouse logs. [[sources/readme/submarine multi-cluster]]
- Latency spike: đo underlay RTT/loss, gateway CPU/NIC, MTU/retransmission rồi CNI/tunnel/application; thứ tự điều chỉnh theo connect/TTFB/trace. [[sources/readme/submarine multi-cluster]]

## Production acceptance

Mục tiêu gồm routes/ports/Broker API thông, requirements pass, candidate HA routable, connections connected, verify pass, DNS/ServiceImport đúng, benchmark latency/throughput lưu và failover đã test. Đây là checklist mục tiêu của nguồn, chưa có ô nào được xác nhận từ tool live. [[sources/readme/submarine multi-cluster]]

Liên quan: [[Kiến trúc Submariner đa VPC]], [[CIDR và Globalnet cho Submariner]], [[Lighthouse và service discovery đa cluster]], [[Đo latency và MTU của Submariner]].
