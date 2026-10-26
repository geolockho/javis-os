---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
**Trạng thái:** đã sửa values.yaml trong repo argocd-deploy-clean (thêm fsGroup 10001, defaultMode 0440), chưa commit và chưa push (thực tế tính đến 2026-10-26).

**Vì sao:** container app chạy runAsUser 10001 nhưng secret volume clusters để 0400, nên khi đọc /etc/kubeconfig-generator/clusters/fsel-prod.yaml báo Permission denied. [[conversations/2026-10-26]]

**Áp dụng:** commit repo argocd-deploy-clean sau khi git pull --rebase, vì image-updater hay tự commit vào repo này. Sau khi Argo sync, kiểm lại pod trên fsel-local. Xem thêm [[argocd-values-kubeconfig-generator-service-4180]].
