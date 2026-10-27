---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-10-27
updated: 2026-10-27
source: [[conversations/2026-10-27]]
---
Khi hai cluster Kubernetes nằm ở nhà cung cấp cloud khác nhau, không nên giả định có private peering giữa hai VPC; cần xác định đường truyền cụ thể: Internet có TLS/mTLS, site-to-site VPN (IPsec hoặc WireGuard), hoặc đường riêng do nhà cung cấp cung cấp [[README-kubernetes-multi-cloud]].

VPN chỉ giải quyết kết nối mạng. VPN không tự đồng bộ service, không tự tạo DNS xuyên cluster và không tự làm ClusterIP từ xa truy cập được [[README-kubernetes-multi-cloud]].

Khi chỉ một số API cần gọi nhau, đề xuất (cần PoC) là gateway HTTPS/mTLS: client gọi vào endpoint gateway của cluster đích, gateway chuyển tới Service rồi Pod. Phải tự quản DNS, chứng thư và quyền truy cập [[README-kubernetes-multi-cloud]]. Khi cần endpoint private thì bổ sung VPN để internal LB hoặc gateway truy cập được [[README-kubernetes-multi-cloud]].

Các lớp cần giải quyết tách biệt: đường truyền, điểm truy cập, discovery, bảo mật, khả năng phục hồi (timeout, health check, failover) [[README-kubernetes-multi-cloud]].

Không có cơ sở xếp hạng hiệu năng giữa các phương án chỉ từ tên sản phẩm; kết quả phụ thuộc đường truyền, MTU và workload thực tế. Cần đo RTT, packet loss và băng thông trên đúng cặp cloud dự kiến, kể cả giờ cao điểm [[README-kubernetes-multi-cloud]]. Mức tương thích của từng cặp cloud chưa được xác nhận (cần xác minh) [[README-kubernetes-multi-cloud]].

Phương án thay thế cần đánh giá thêm: Skupper, đưa service từ xa vào qua Service cục bộ và chỉ định rõ service được chia sẻ [[README-kubernetes-multi-cloud]].
