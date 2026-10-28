---
type: business
provenance: user
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
User khẳng định cert-manager trên cluster đã tự sinh cert cho tls.hosts của Ingress [[conversations/2026-10-28]]. Chưa kiểm tra annotation cert-manager.io/cluster-issuer hay default issuer trên từng cluster, cần chạy lệnh đọc kubectl get ingress để xác minh (cần xác minh) [[conversations/2026-10-28]].
