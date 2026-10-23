---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
User chốt ngày 2026-10-23: dev thường được thêm vào project GitLab chứ không vào group, nên quyền xin namespace không được phụ thuộc group. App bỏ việc so group và header X-Forwarded-Groups. Danh sách namespace theo cluster (ConfigMap kubeconfig-generator-namespaces) là whitelist. Đây là thay đổi so với [[kien-truc-kubeconfig-generator-da-duyet]].

**Vì sao:** dev được add vào project, không phải group.

**Áp dụng:** khi thêm namespace, sửa danh sách rồi chạy lại RBAC, xem skill them-namespace-kubeconfig. Domain email cho oauth2-proxy (đang --email-domain=*) chưa chốt.
