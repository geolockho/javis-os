---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Argo CD Multi-Cluster", "Cluster onboarding"]
source: ["[[sources/readme/argocd-cluster-manager]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Argo CD đa cluster

## Xác nhận của người dùng ngày 2026-10-07

`kpi-k8s-uat` là tên cũ tương ứng `kpi-uat`; dùng `kpi-uat` trong nội dung vận hành của wiki. `fsel-premium` là context khác, chưa đi vào sử dụng; không đồng nhất với `fsel-pt-teacher` và không coi là context active đã được liệt kê live. [[sources/readme/open-questions-answers-2026-10-07]]

Argo CD đa cluster là mô hình GitOps với Argo CD ở management cluster kết nối trực tiếp API Kubernetes của target cluster. Trang này chưng cất quy trình thiết lập, không xác nhận hệ thống đã được triển khai. [[sources/readme/argocd-cluster-manager]]

## Kiến trúc và điều kiện

Luồng thiết kế là Git -> Argo CD -> API HTTPS 443/6443 -> target; nguồn không yêu cầu cài Argo CD Agent ở target. `cluster add` dùng context local tạo SA/RBAC trên target, lưu credential thành Secret trong namespace `argocd`. [[sources/readme/argocd-cluster-manager]]

Cả máy CLI và Pod `argocd-application-controller` phải thông DNS/TCP/TLS tới API target. CLI truy cập được chưa chứng minh controller truy cập được; HTTP 401 trong test network không credential chỉ chứng minh API trả lời, chưa chứng minh auth. [[sources/readme/argocd-cluster-manager]]

## Vòng đời cluster (quy trình tham chiếu)

1. Nhận kubeconfig, test từng file/context, hợp nhất và đổi tên rõ ràng nếu cần. [[sources/readme/argocd-cluster-manager]]
2. Login CLI, ví dụ nguồn dùng `--grpc-web`; đăng ký đúng context bằng `argocd cluster add`. [[sources/readme/argocd-cluster-manager]]
3. Kiểm tra SA/RBAC ở target và Cluster Secret ở management; gắn labels, giới hạn AppProject, chọn cluster qua ApplicationSet. [[sources/readme/argocd-cluster-manager]]
4. Verify cluster `Successful`, Application được generate, `Synced`/`Healthy`, resource ở đúng target và không ở nhầm cluster. Các trạng thái này là tiêu chí, không phải kết quả live của lần ingest. [[sources/readme/argocd-cluster-manager]]

Lệnh tham chiếu; `cluster add` tạo credential/RBAC, không phải lệnh chỉ đọc: [[sources/readme/argocd-cluster-manager]]

```bash
argocd cluster add <CONTEXT> --name <CLUSTER_NAME> --kubeconfig <FILE>
argocd cluster list
argocd app get <APP>
kubectl --context=<TARGET> -n <NAMESPACE> get deployment,pod,service
```

Trước `cluster rm`, kiểm tra app dùng destination đó. Chỉ dọn SA/ClusterRole/Binding khi target không còn app được quản lý; finalizer Application có thể kéo theo xóa tài nguyên target. Backup cần gồm Application, ApplicationSet, AppProject, Repository/Cluster Secret, `argocd-cm`, `argocd-rbac-cm`, `argocd-secret`; backup Secret phải được bảo vệ và mã hóa. [[sources/readme/argocd-cluster-manager]]

## Tên trong ví dụ

Nguồn gốc dùng `fsel-prod`, `fsel-premium`, `guruit`, xen tên cũ `kpi-k8s-uat`. Tên cũ được giữ tại mô tả lịch sử để truy vết; phần vận hành dùng tên người dùng chốt ở trên. Endpoint ví dụ không thay dữ liệu live. [[sources/readme/argocd-cluster-manager]]

Liên quan: [[Quản lý kubeconfig nhiều cluster]], [[Phân quyền và credential Argo CD]], [[ApplicationSet và GitOps đa cluster]].
