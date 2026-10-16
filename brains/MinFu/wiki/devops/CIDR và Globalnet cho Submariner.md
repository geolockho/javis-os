---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Submariner CIDR planning", "Globalnet", "Pod CIDR overlap", "Service CIDR"]
source: ["[[sources/readme/submarine multi-cluster]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# CIDR và Globalnet cho Submariner

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận hiện chưa triển khai Submariner. Các thiết kế/checklist/ví dụ bên dưới là tài liệu tham khảo. Chỉ hỏi và kiểm chứng compatibility, route, ports, NAT, encryption, CIDR, Broker khi người dùng cần triển khai; không coi các mục này đã pass hoặc tự tạo việc theo dõi. [[sources/readme/open-questions-answers-2026-10-07]]

Thiết kế CIDR Submariner quyết định có thể route trực tiếp Pod/Service hay cần Globalnet khi dải IP overlap. Trang này ghi ví dụ planning trong nguồn ngày 2026-08-12, không phải CIDR live của các cluster. [[sources/readme/submarine multi-cluster]]

## Pool và chia dải (ví dụ)

Nguồn gọi Pod pool 100.96.0.0/11 và Service pool 100.64.0.0/13 là dải FPT khuyến nghị. Không cấp nguyên cùng pool cho cả hai cluster khi dùng non-Globalnet; cần kiểm tra constraint Portal/API FPT trước khi tạo. [[sources/readme/submarine multi-cluster]]

Ví dụ A: Pod 100.96.0.0/14, Service 100.64.0.0/16; B: Pod 100.100.0.0/14, Service 100.65.0.0/16. VPC/node/gateway subnet ví dụ A 10.10.0.0/16 và 10.10.10.0/24, B 10.20.0.0/16 và 10.20.10.0/24. Đây không phải IP đã kiểm tra. [[sources/readme/submarine multi-cluster]]

Nguồn chia Pod /11 thành 8 block /14 từ 100.96 tới 100.124 với bước 4 ở octet thứ hai; Service /13 thành 8 block /16 từ 100.64 tới 100.71. Ngoài khác nhau giữa cluster, cần tránh conflict VPC/node/Pod/Service trong routing domain. [[sources/readme/submarine multi-cluster]]

## Quyết định Globalnet

Nguồn đề xuất non-Globalnet nếu thiết kế được CIDR không overlap; nếu bắt buộc cùng CIDR, dùng Broker với Globalnet rồi join các cluster. Đây là nhánh thiết kế, không xác nhận Globalnet được bật. [[sources/readme/submarine multi-cluster]]

```bash
subctl show networks --context cluster-a
subctl show networks --context cluster-b
```

Các lệnh nguồn dùng để khảo sát networks; prefix /14 và /16 hợp lệ về planning không chứng minh FKE chấp nhận kích thước đó. [[sources/readme/submarine multi-cluster]]

Liên quan: [[Kiến trúc Submariner đa VPC]], [[Triển khai và khám lỗi Submariner]], [[Lighthouse và service discovery đa cluster]].
