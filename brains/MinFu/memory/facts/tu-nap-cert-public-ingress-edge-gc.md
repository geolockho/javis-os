---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Ngày 2026-10-28 user bỏ annotation `cert-manager.io/cluster-issuer` khỏi Ingress edge trên gc và nói sẽ tự cài cert public [[conversations/2026-10-28]].

**Vì sao:** user muốn tự quản cert public. Lý do cụ thể chưa được nêu.

**Áp dụng:** Ingress edge chỉ có khối `tls` tham chiếu Secret `api-example-com-tls` do user tạo tay trong namespace `edge`. Bản này áp dụng cho bậc 0, 1 và 2 của workspace/gc-sc-gateway. Cert-manager với CA nội bộ ở bậc 1 và 2 vẫn giữ, vì user chưa phản đối đề xuất này (cần xác minh). Khác với [[cert-manager-tu-cap-cert-tls-hosts]], vốn mô tả cluster hiện tại, bản này là quyết định cho Ingress edge mới.
