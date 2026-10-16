---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["FKE admin kubeconfig", "Long-lived ServiceAccount token", "fke-admin", "TokenRequest"]
source: ["[[sources/readme/Create_ServiceAccount_Kubeconfig]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Kubeconfig ServiceAccount cho FPT FKE

## Xác nhận của người dùng ngày 2026-10-07

Người dùng trả lời "có" cho việc CA trong Secret ServiceAccount khớp TLS API endpoint FKE bên ngoài. Đây là xác nhận từ người dùng, chưa có lần kiểm tra độc lập trong phiên cập nhật; không suy ra token TTL hoặc tình trạng live của từng credential. [[sources/readme/open-questions-answers-2026-10-07]]

Nguồn FPT FKE mô tả bootstrap ServiceAccount từ kubeconfig portal còn hiệu lực để tạo bearer-token kubeconfig độc lập với certificate client ngắn hạn. Đây là hướng dẫn, không chứng minh các context FKE của người dùng đã áp dụng. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

## Bài toán

Ví dụ portal/Gardener certificate có notBefore 2026-09-03, notAfter 2026-09-04, khoảng 24 giờ. Không suy mọi credential FKE đều cùng hạn; phải đọc certificate thực tế. Mục tiêu là dùng kubectl/Lens/jump host sau khi certificate portal cũ hết hạn. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

## Bootstrap (quy trình nguồn)

1. Test context/API bằng kubeconfig FPT còn hiệu lực. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
2. Tạo SA, ví dụ `kube-system/fke-admin`, và RBAC đúng nhu cầu; cluster-admin chỉ nếu thực sự cần. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
3. Tạo Secret kiểu `kubernetes.io/service-account-token`, annotation trỏ SA, đợi controller điền token/CA. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
4. Lấy API endpoint, token, CA rồi dựng file riêng bằng set-cluster/set-credentials/set-context/use-context; Linux chmod 600. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
5. Test nodes, `/version`, whoami/can-i; identity dự kiến `system:serviceaccount:kube-system:fke-admin`. Kiểm chứng lại khi cert portal hết hạn là tiêu chí, chưa có bằng chứng trong lần ingest. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fke-admin-token
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: fke-admin
type: kubernetes.io/service-account-token
```

Manifest trên là mẫu từ nguồn, tạo credential dài hạn chứ không phải test chỉ đọc. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

## Token và RBAC

Nguồn phân biệt manual Secret token dài hạn với `kubectl create token` qua TokenRequest có hạn. Tài liệu mô tả từ Kubernetes 1.24 không tự tạo Secret token cho mọi SA, nên SECRETS=0 không tự chỉ ra lỗi; cần đối chiếu version khi áp dụng. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

Tách SA admin, Argo CD, monitoring read-only và CI theo namespace. Không chia một token admin cho tất cả; không commit kubeconfig hoặc gửi token qua chat, rotate khi lộ; human access ưu tiên OIDC/SSO nếu có hỗ trợ. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

## Rotate, revoke và lỗi

Nguồn dùng xóa Secret để revoke, tạo lại Secret/đợi token/dựng kubeconfig để rotate. Dọn hoàn toàn gồm Secret, Binding và SA; các thao tác này đổi quyền truy cập. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

- Token chưa có: kiểm tra Secret type/annotation, SA và controller populate. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
- Unauthorized: kiểm tra token/Secret/SA. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
- Forbidden: tập trung RBAC và can-i theo nguồn. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
- Unknown authority: đối chiếu CA/certificate API, không che bằng insecure-skip-tls-verify. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

Nguồn ưu tiên CA từ Secret SA. Tại lúc ingest ban đầu chưa có xác nhận về endpoint; người dùng đã xác nhận sự khớp CA ngày 2026-10-07 như mục trên. Dựng file thành công vẫn chưa tự chứng minh auth/credential hiện còn hiệu lực. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

Liên quan: [[Quản lý kubeconfig nhiều cluster]], [[Gia hạn certificate kubeconfig bằng kubeadm]], [[Phân quyền và credential Argo CD]].
