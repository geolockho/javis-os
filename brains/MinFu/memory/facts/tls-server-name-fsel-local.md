---
type: reference
provenance: source
origin: javis-learned
created: 2026-10-26
updated: 2026-10-26
---
Kubeconfig `fsel-local.yaml` trong secret `kubeconfig-generator-clusters` (namespace `fsel-internal-tools`) trỏ `server: https://101.99.7.167:6444` nhưng không có `tls-server-name: 10.10.0.182`. Cert API server chỉ có SAN `10.10.0.182`, `10.96.0.1`, `k8s-master` và `kubernetes*`, không có `101.99.7.167` (thực tế tính đến 2026-10-26) [[conversations/2026-10-26]]. Thiếu dòng này, app báo CERTIFICATE_VERIFY_FAILED và giữ danh mục namespace cũ thay vì đọc label [[conversations/2026-10-26]]. Kubeconfig trên máy dev chạy được vì có dòng tls-server-name đó [[conversations/2026-10-26]].
