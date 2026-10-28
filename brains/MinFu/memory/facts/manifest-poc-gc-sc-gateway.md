---
superseded_by: manifest-gc-sc-tach-thu-muc-theo-bac
type: business
provenance: source
origin: javis-learned
created: 2026-10-27
updated: 2026-10-27
---
Javis đã viết bộ manifest PoC cho đường gc → sc tại `workspace/gc-sc-gateway/` (thực tế tính đến 2026-10-27), chia ba thư mục `shared/`, `sc/`, `gc/` kèm README thứ tự apply (ghi nhận 2026-10-27). [[conversations/2026-10-27]]

- Còn các chỗ TODO chưa điền: annotation LB internal của NCC, dải IP nguồn thật mà sc nhìn thấy từ gc, IP internal LB của sc trong `gc/01`, tên namespace và Service backend.
- Đợt PoC đầu nên bỏ `whitelist-source-range` và `auth-tls-*`, bật mTLS sau khi đường mạng đã thông (mục tiêu, chưa làm).
- Cách gọi trực tiếp Service (không qua ingress) chưa có manifest, xem [[muon-goi-service-sc-truc-tiep-tu-gc]].

Liên quan: [[ke-hoach-tach-gateway-va-service-nhieu-cluster]], [[bac-bao-mat-gc-sc]].


## Lịch sử
- [2026-10-28] Bị thay thế bởi [[manifest-gc-sc-tach-thu-muc-theo-bac]] (user đổi thông tin).
