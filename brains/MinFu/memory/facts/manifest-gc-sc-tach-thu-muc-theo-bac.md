---
type: reference
provenance: user
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Bộ manifest nằm tại workspace/gc-sc-gateway/, có README tổng quan và 3 thư mục bac-0, bac-1, bac-2 [[conversations/2026-10-28]]. Mỗi bậc có gc/, sc/ và README riêng [[conversations/2026-10-28]].

Bậc 0: LB internal trên sc mở cổng 80, Ingress edge trên gc dùng backend-protocol HTTP và bỏ proxy-ssl-* [[conversations/2026-10-28]].

Còn TODO: CIDR whitelist (10.10.0.0/16 là giả định, cần xác minh), tên annotation LB internal và tên issuer cert-manager [[conversations/2026-10-28]]. Thứ tự nâng cấp 0 → 1 → 2 theo README của từng bậc [[conversations/2026-10-28]].
