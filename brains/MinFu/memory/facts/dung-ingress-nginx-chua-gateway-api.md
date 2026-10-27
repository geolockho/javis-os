---
type: business
provenance: user
origin: javis-learned
created: 2026-10-27
updated: 2026-10-27
---
Ngày 2026-10-27 người dùng nói tạm thời chưa dùng được Gateway API và vẫn đang dùng ingress-nginx ([[conversations/2026-10-27]]).

**Vì sao:** đây là ràng buộc hiện tại khi bàn kế hoạch tách gateway và service sang cluster riêng ([[ke-hoach-tach-gateway-va-service-nhieu-cluster]]). Người dùng muốn giữ ingress-nginx ở cả hai tầng.

**Áp dụng:** khi bàn kế hoạch này, không đề xuất Gateway API hay Envoy Gateway làm phương án mặc định, trừ khi người dùng hỏi lại.
