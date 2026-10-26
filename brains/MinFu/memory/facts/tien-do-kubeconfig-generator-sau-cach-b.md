---
superseded_by: kubeconfig-generator-da-push-va-deploy-fsel-local
type: business
provenance: assistant
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Theo báo cáo của Javis (thực tế tính đến 2026-10-23, chưa kiểm lại trên cluster): code app đã chuyển sang cách B, 89 test qua và 1 test bỏ qua (cần cluster thật), đã robocopy sang repo D:\FSEL\other-services\kubeconfig-generator ([[conversations/2026-10-23]]). Thư mục values ArgoCD D:\argocd-deploy-clean\values\fsel-internal-tools\kubeconfig-generator đã bỏ ConfigMap group-map, Service và Ingress trỏ cổng 4180 (oauth2-proxy), chart render được bằng helm template. Chưa commit, chưa push, chưa sync lên cluster nào. Còn mở: đổi selector NetworkPolicy từ app.kubernetes.io/name sang app.kubernetes.io/instance cho khớp chart fsel; khi commit repo argocd-deploy-clean chỉ add thư mục kubeconfig-generator vì repo đó còn thay đổi khác. Giữ nguyên .gitignore theo chốt của người dùng ([[robocopy-thieu-xo-ghi-de-gitignore]]). Việc apply lên fsel-prod và fsel-local là mục tiêu, chưa làm.


## Lịch sử
- [2026-10-26] Bị thay thế bởi [[kubeconfig-generator-da-push-va-deploy-fsel-local]] (user đổi thông tin).
