---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Submariner Multi-Cluster", "FPT VPC networking", "Submariner Gateway", "East-west networking"]
source: ["[[sources/readme/submarine multi-cluster]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Kiến trúc Submariner đa VPC

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận hiện chưa triển khai Submariner. Các thiết kế/checklist/ví dụ bên dưới là tài liệu tham khảo. Chỉ hỏi và kiểm chứng compatibility, route, ports, NAT, encryption, CIDR, Broker khi người dùng cần triển khai; không coi các mục này đã pass hoặc tự tạo việc theo dõi. [[sources/readme/open-questions-answers-2026-10-07]]

Submariner trong nguồn là thiết kế kết nối Pod/Service giữa hai cluster ở hai VPC FPT Cloud qua đường private subnet. Tài liệu tổng hợp ngày 2026-08-12; các topology là mục tiêu/khuyến nghị, không chứng minh đã cài hoặc đang dùng cho KPI. [[sources/readme/submarine multi-cluster]]

## Tách hai luồng

Broker là control plane trao đổi Cluster/Endpoint/ServiceImport/EndpointSlice và metadata, không chuyển packet ứng dụng. Một cluster chứa Broker vẫn phải join như participant; các cluster khác cần truy cập được Kubernetes API của Broker. [[sources/readme/submarine multi-cluster]]

Data plane theo nguồn: Pod -> Route Agent -> active Gateway local -> tunnel -> Gateway remote -> Pod/Service. Route Agent chạy trên nodes, Gateway ở node label `submariner.io/gateway=true`; Lighthouse làm service discovery. [[sources/readme/submarine multi-cluster]]

Nguồn đề xuất ít nhất hai gateway candidate mỗi cluster, active/passive và một active tại một thời điểm. HA tăng availability, không biến hai gateway thành active-active chia tải; traffic vẫn tập trung tại active gateway. [[sources/readme/submarine multi-cluster]]

## Constraint FPT và lựa chọn tunnel

Nguồn trích phản hồi FPT "chỉ hỗ trợ kết nối 2 subnet giữa 2 VPC". Thiết kế có điều kiện: tất cả gateway candidate nằm subnet routable, private IP L3 hai chiều, firewall phù hợp, và route riêng tới API Broker; không cần mọi worker cross-VPC thông trực tiếp. Các điều kiện này cần xác nhận với FPT, chưa phải bằng chứng kết nối thật. [[sources/readme/submarine multi-cluster]]

Nguồn chọn VXLAN khi private reachability, không NAT và underlay security phù hợp; VXLAN được mô tả không mã hóa. Nếu private path không encrypt mà cần confidentiality, nguồn cân nhắc libreswan/wireguard. Không suy "private" đồng nghĩa "encrypted". [[sources/readme/submarine multi-cluster]]

## Port theo thiết kế nguồn

- Gateway liên cluster: UDP 4490 cho endpoint/NAT discovery, UDP 4500 cho tunnel trong mẫu. [[sources/readme/submarine multi-cluster]]
- Node -> gateway nội cluster: UDP 4800 cho internal VXLAN. [[sources/readme/submarine multi-cluster]]
- Gateway metrics nếu dùng: TCP 8080. [[sources/readme/submarine multi-cluster]]

Các port, driver/flag và compatibility phải đối chiếu phiên bản pin trước triển khai; nguồn không nêu phiên bản Submariner cụ thể, không coi port 4500 là bất biến cho mọi driver/config. [[sources/readme/submarine multi-cluster]]

## Phạm vi sản phẩm

Submariner xử lý east-west; north-south chọn cluster gần/khỏe còn cần GeoDNS/GSLB, health check, DNS/LB failover và state/database strategy. Cross-cluster service call không đi mặc định qua external FPT LB/Ingress theo kiến trúc nguồn. [[sources/readme/submarine multi-cluster]]

Nguồn khuyên giữ service local và cross-cluster khi cần, vì remote dependency tăng coupling giữa failure domains, nhạy latency và phạm vi ảnh hưởng. [[sources/readme/submarine multi-cluster]]

Liên quan: [[CIDR và Globalnet cho Submariner]], [[Triển khai và khám lỗi Submariner]], [[Lighthouse và service discovery đa cluster]], [[Đo latency và MTU của Submariner]].
