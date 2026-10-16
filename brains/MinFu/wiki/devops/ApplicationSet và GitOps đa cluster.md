---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["ApplicationSet", "Git Files Generator", "Cluster Generator", "Matrix Generator", "App of Apps"]
source: ["[[sources/readme/argocd-cluster-manager]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# ApplicationSet và GitOps đa cluster

## Xác nhận của người dùng ngày 2026-10-07

Người dùng chọn `git.files` làm quy ước generator cho các mẫu đọc file values. Câu hỏi về tên Directory/Files đã giải quyết; đường dẫn `helm.valueFiles`, quyền guestbook repo/namespace và labels `prod`/`production` chưa được trả lời, tiếp tục giữ mở. [[sources/readme/open-questions-answers-2026-10-07]]

ApplicationSet tạo các Application từ dữ liệu Git và cluster đăng ký trong Argo CD. Đây là các mẫu thiết kế trong nguồn, chưa có bằng chứng apply thành công. [[sources/readme/argocd-cluster-manager]]

## Chọn generator

- Git files đọc `services/*/values-prod.yaml` cho mỗi service; mẫu dùng `goTemplate: true`, `missingkey=error`, requeue 60 giây. [[sources/readme/argocd-cluster-manager]]
- Cluster chọn labels Secret và truyền `.name`, `.nameNormalized`, `.server`, `.metadata.labels`; phù hợp cùng platform app trên nhiều cluster. [[sources/readme/argocd-cluster-manager]]
- Matrix ghép Git x Cluster; ví dụ 3 service x 2 cluster tạo 6 Application, không phải số app live. [[sources/readme/argocd-cluster-manager]]
- Destination từ values dùng `application.name`, `application.environment`, `destination.clusterName`, `destination.namespace` để chọn app/chart/target; values cần review/schema validation. [[sources/readme/argocd-cluster-manager]]

## GitOps và bootstrap

Nguồn tách `projects/`, `applicationsets/`, `template/stage/<environment>`, `services/<service>/values-<environment>.yaml`. Root Application quản lý bootstrap/AppProject/ApplicationSet qua Git sau lần apply đầu. Webhook GitLab tới `/api/webhook` chỉ refresh; auto-sync vẫn cần `syncPolicy.automated`. [[sources/readme/argocd-cluster-manager]]

Các mẫu dùng prune/selfHeal/CreateNamespace; có mẫu thêm PruneLast, ApplyOutOfSyncOnly, retry 5 lần với backoff 5s/factor 2/max 3m. Đây là cấu hình đề xuất, cần xét quyền và tác động prune trước triển khai. [[sources/readme/argocd-cluster-manager]]

## Verify và lỗi

Kiểm tra Git pattern/repo credential -> selector labels -> field Go template -> destination đúng tên đăng ký -> AppProject cho phép -> Application generate -> Synced/Healthy -> resource đúng target. AppSet không generate thường liên quan pattern, labels, missing key, credential hoặc render; `InvalidSpecError` cần so destination với danh sách cluster. [[sources/readme/argocd-cluster-manager]]

```bash
kubectl -n argocd describe applicationset <NAME>
kubectl -n argocd logs deploy/argocd-applicationset-controller --since=15m
kubectl -n argocd get applications
argocd app get <APP>
```

Các lệnh trên chưng cất từ mục verify/troubleshooting của nguồn. Khi dọn app, kiểm tra ownerReferences và finalizer vì có thể xóa resource target. [[sources/readme/argocd-cluster-manager]]

## Mâu thuẫn đã chốt và mẫu còn cần xác minh

Nguồn mục 13 ghi "Git Directory Generator" nhưng YAML dùng `git.files`; giữ khác biệt lịch sử trong nguồn để truy vết. [[sources/readme/argocd-cluster-manager]]

Các mẫu valueFiles dùng `../../../{{ .path.path }}` với generator đọc file. Cần xác minh đường dẫn đầy đủ và parameter filename theo version/chart; chưa coi YAML là mẫu chạy được nguyên trạng. Labels `prod` và `production` trong cùng nguồn cũng cần chuẩn hóa khi triển khai. [[sources/readme/argocd-cluster-manager]]

Liên quan: [[Argo CD đa cluster]], [[Phân quyền và credential Argo CD]], [[Lighthouse và service discovery đa cluster]].
