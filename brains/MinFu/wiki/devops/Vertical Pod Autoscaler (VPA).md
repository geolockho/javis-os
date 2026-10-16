---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-10-08
updated: 2026-10-08
source: [[conversations/2026-10-08]]
---
## Tóm tắt
Vertical Pod Autoscaler (VPA) tự đề xuất hoặc tự điều chỉnh `requests` CPU/memory cho container dựa trên mức dùng thực tế [[conversations/2026-10-08]].

## Đối tượng áp dụng
- VPA KHÔNG gắn vào đối tượng `Service`. `targetRef` trỏ đến controller tạo Pod phía sau Service như `Deployment` hoặc `StatefulSet` [[conversations/2026-10-08]].
- Resource nên được quản lý ở từng container (`containerPolicies` theo `containerName`). Workload dùng Pod-level resources chưa được VPA hỗ trợ đầy đủ (cần xác minh) [[conversations/2026-10-08]].

## Thành phần
- `vpa-recommender`: tính khuyến nghị tài nguyên [[Kiến trúc VPA]].
- `vpa-updater`: quyết định cập nhật (evict) Pod [[Kiến trúc VPA]].
- `vpa-admission-controller`: gán tài nguyên khi Pod được tạo [[Kiến trúc VPA]].
- VPA cần Metrics Server; kiểm tra bằng `kubectl get apiservice v1beta1.metrics.k8s.io` và `kubectl top pods -A` [[conversations/2026-10-08]].

## Tương thích phiên bản
Thực tế tính đến 2026-10-08, theo tài liệu cài đặt VPA [[Tài liệu cài đặt VPA]]:
- Kubernetes 1.36 đến 1.38: VPA 1.8.x.
- Kubernetes 1.35 đến 1.37: VPA 1.7.x.
- Kubernetes 1.34 đến 1.36: VPA 1.6.x.
- Không dùng nhánh `master` để cài production [[Tài liệu cài đặt VPA]].
- Với cluster cũ hơn như Kubernetes 1.25 phải chọn nhánh VPA cũ tương ứng trong bảng tương thích; nhánh cụ thể (cần xác minh) [[conversations/2026-10-08]].

## Quy trình triển khai an toàn
1. Cài bằng `git clone --branch vpa-release-<x.y>` repo `kubernetes/autoscaler`, chạy `vertical-pod-autoscaler/hack/vpa-up.sh` (trên Windows dùng WSL hoặc Git Bash có `openssl`) [[conversations/2026-10-08]].
2. Tạo VPA với `updateMode: "Off"` để chỉ thu thập khuyến nghị [[conversations/2026-10-08]].
3. Đặt `controlledValues: RequestsOnly` để VPA chỉ đổi `requests`, giữ `limits` theo manifest; đặt `minAllowed`/`maxAllowed` làm biên [[conversations/2026-10-08]].
4. Khi khuyến nghị ổn định mới chuyển sang `Recreate`, chế độ này có thể evict và tạo lại Pod [[conversations/2026-10-08]].

## Liên quan
- [[devops/Quản lý kubeconfig nhiều cluster]]
