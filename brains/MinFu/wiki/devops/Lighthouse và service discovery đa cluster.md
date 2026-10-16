---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["ServiceExport", "ServiceImport", "clusterset.local", "Lighthouse DNS"]
source: ["[[sources/readme/submarine multi-cluster]]", "[[sources/readme/open-questions-answers-2026-10-07]]"]
---

# Lighthouse và service discovery đa cluster

## Xác nhận của người dùng ngày 2026-10-07

Người dùng xác nhận hiện chưa triển khai Submariner. Các thiết kế/checklist/ví dụ bên dưới là tài liệu tham khảo. Chỉ hỏi và kiểm chứng compatibility, route, ports, NAT, encryption, CIDR, Broker khi người dùng cần triển khai; không coi các mục này đã pass hoặc tự tạo việc theo dõi. [[sources/readme/open-questions-answers-2026-10-07]]

Lighthouse trong Submariner cung cấp discovery service giữa các cluster qua Broker metadata và DNS clusterset.local. Nội dung theo tài liệu 2026-08-12, chưa xác nhận service nào đang export live. [[sources/readme/submarine multi-cluster]]

## Chuỗi metadata và DNS

Nguồn mô tả ServiceExport -> Lighthouse Agent -> Broker -> remote Lighthouse -> ServiceImport/EndpointSlice -> Lighthouse DNS. Broker API phải reachable độc lập với data plane gateway tunnel. [[sources/readme/submarine multi-cluster]]

ServiceExport phải cùng tên/namespace Service gốc. Ví dụ backend/user-api port 8080 được gọi bằng user-api.backend.svc.clusterset.local, hoặc cluster-b.user-api.backend.svc.clusterset.local để chọn cluster cụ thể. [[sources/readme/submarine multi-cluster]]

```yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: user-api
  namespace: backend
```

Manifest mẫu từ nguồn có thể do GitOps/Argo CD quản lý cùng Service, nhưng cần RBAC/AppProject cho CRD/resource tương ứng. [[sources/readme/submarine multi-cluster]] [[sources/readme/argocd-cluster-manager]]

## Verify chuỗi, không chỉ tunnel

```bash
kubectl --context cluster-b -n backend get serviceexport user-api
kubectl --context cluster-a -n backend get serviceimport user-api
kubectl --context cluster-a get endpointslices -A -l multicluster.kubernetes.io/service-name=user-api
```

Theo nguồn, sau các kiểm tra trên cần resolve DNS và gọi service từ Pod test. Pod curl-test và URL là ví dụ; verify phải có cả non-gateway Pod, không chỉ từ gateway. [[sources/readme/submarine multi-cluster]]

Nguồn mô tả ưu tiên local khi service cùng tên/namespace export ở cả hai cluster; behavior healthy/remote và cluster-specific DNS cần đối chiếu version trước dựa vào để cân bằng/failover. Đây chưa phải kết quả test hệ thống. [[sources/readme/submarine multi-cluster]]

## Khi import/DNS thiếu

Kiểm tra ServiceExport đúng tên/namespace, Broker API/metadata, Lighthouse logs, CoreDNS block clusterset.local:53, ServiceImport và EndpointSlice. Connections connected không tự chứng minh chuỗi discovery đầy đủ. [[sources/readme/submarine multi-cluster]]

Liên quan: [[Kiến trúc Submariner đa VPC]], [[Triển khai và khám lỗi Submariner]], [[ApplicationSet và GitOps đa cluster]], [[Đo latency và MTU của Submariner]].
