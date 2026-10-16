---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["Argo CD RBAC", "AppProject", "Cluster Secret", "argocd-manager"]
source: ["[[sources/readme/argocd-cluster-manager]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Phân quyền và credential Argo CD

## Xác nhận của người dùng ngày 2026-10-07

Quy ước người dùng chốt: app triển khai trên chính cluster cài Argo CD dùng project `default`; app ở cluster khác nên dùng project có tên tương ứng cluster. Đây là quy ước vận hành được người dùng xác nhận, chưa phải bằng chứng RBAC/AppProject đã cấu hình live. [[sources/readme/open-questions-answers-2026-10-07]]

Phân quyền Argo CD đa cluster gồm credential API target và chính sách AppProject giới hạn repo/destination/resource. Nội dung là thiết kế từ nguồn, chưa xác nhận RBAC live. [[sources/readme/argocd-cluster-manager]]

## Hai lớp quyền

Nguồn mô tả `kube-system/argocd-manager`, ClusterRole `argocd-manager-role` và Binding tương ứng ở target. Admin kubeconfig dùng bootstrap, runtime dùng SA riêng. AppProject giới hạn `sourceRepos`, `destinations`, cluster/namespace resource whitelist và cảnh báo orphan; SA vẫn cần quyền thực thi resource đó. [[sources/readme/argocd-cluster-manager]]

Nguồn dùng lặp `--namespace` và `--cluster-resources=false` để giới hạn đăng ký. Nếu app cần quản lý CRD, StorageClass, ClusterIssuer, ClusterRole/Binding hoặc webhook cấp cluster, phải xét quyền tương ứng. Khi Forbidden, kiểm tra thiếu quyền nào thay vì cấp cluster-admin ngay. [[sources/readme/argocd-cluster-manager]]

## Cluster Secret và selector

Secret trong namespace `argocd` mang label `argocd.argoproj.io/secret-type=cluster`, dữ liệu ví dụ gồm `name`, `server`, JSON `config` với bearer token/CA. Secret/backup chứa token không commit dạng rõ; nguồn đề cập SOPS, Sealed Secrets, External Secrets và Vault. [[sources/readme/argocd-cluster-manager]]

Cluster Generator chọn labels Secret như environment/provider/region/workload/enabled. Mẫu dùng `environment=prod` cho FPT nhưng `environment=production` cho guruit; selector `prod` không khớp giá trị `production`, nên cần review phạm vi. [[sources/readme/argocd-cluster-manager]]

Lệnh chẩn đoán tham chiếu: [[sources/readme/argocd-cluster-manager]]

```bash
argocd cluster list
kubectl -n argocd get secret -l argocd.argoproj.io/secret-type=cluster --show-labels
kubectl --context=<TARGET> auth can-i create deployments -n <NAMESPACE> --as=system:serviceaccount:kube-system:argocd-manager
kubectl -n argocd logs statefulset/argocd-application-controller --since=15m
```

## TLS và Unknown

Unknown cần kiểm tra route từ controller, DNS, firewall, token và TLS. Nguồn yêu cầu API hostname đúng SAN/CA; không dùng certificate HTTP Ingress thay API certificate khi TCP proxy chưa đúng. `curl -k` trong ví dụ chỉ bỏ verify TLS, không chứng minh trust CA/SAN đúng. [[sources/readme/argocd-cluster-manager]]

Mẫu `cluster add ... --insecure` được nguồn đưa như workaround; phạm vi cờ đối với CLI/Argo CD server/target API cần xác minh theo version, chưa coi là sửa được TLS target. [[sources/readme/argocd-cluster-manager]]

## Mâu thuẫn đã được người dùng định hướng

Mục 11/21 khuyến nghị không để toàn bộ app trong project `default` và tách production/non-production. Mục 17 dùng default cho Root Application; mục 30 tạo `fsel-prod-network` với `--project default`, không giải thích ngoại lệ. Đây là khác biệt được ghi nhận khi ingest; giữ lại cả khuyến nghị và ví dụ gốc để truy vết. [[sources/readme/argocd-cluster-manager]]

Quyết định ngày 2026-10-07: dùng `default` cho app trên cluster cài Argo CD; với remote cluster nên đặt project theo tên cluster. Quyết định giải thích phạm vi áp dụng trong brain, không sửa nguồn gốc và không tự áp thay đổi lên cluster. [[sources/readme/open-questions-answers-2026-10-07]]

AppProject mẫu cho repo GitLab/namespace định trước, nhưng test guestbook dùng repo GitHub và `argocd-test`; cần quyền bổ sung tương ứng, không coi manifest test chạy được nguyên trạng. [[sources/readme/argocd-cluster-manager]]

Liên quan: [[Argo CD đa cluster]], [[ApplicationSet và GitOps đa cluster]], [[Kubeconfig ServiceAccount cho FPT FKE]].
