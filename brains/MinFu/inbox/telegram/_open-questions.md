# Open Questions

Questions the wiki cannot fully answer yet. One per line:
- [ ] (YYYY-MM-DD) [[Topic]]: question or gap - status: open
- [ ] (2026-10-06) Giao tiếp với partner/cộng sự: chưa có nguồn về vai trò, cách phối hợp và tình huống cụ thể của người dùng; cần làm rõ để tư vấn theo ngữ cảnh. status: open

## Ingest tài liệu readme, 2026-10-07

- [ ] (2026-10-07) [[wiki/devops/Phân quyền và credential Argo CD]]: Mâu thuẫn: mục 11/21 khuyến nghị hạn chế project default, nhưng mục 17/30 dùng default cho bootstrap/fsel-prod-network. Ngoại lệ/chính sách nào được chấp nhận? [[sources/readme/argocd-cluster-manager]] status: open
answer: các app triển khai nằm trên cluster cài argocd thì dùng project default, còn các app nằm ở cluster khác thì nên đặt ở project tên tương ứng cluster
- [ ] (2026-10-07) [[wiki/devops/ApplicationSet và GitOps đa cluster]]: Mâu thuẫn tên generator: mục 13 ghi Git Directory nhưng manifest dùng git.files. Chọn quy ước nào để duy trì wiki? [[sources/readme/argocd-cluster-manager]] status: open
dùng git.files
- [ ] (2026-10-07) [[wiki/devops/ApplicationSet và GitOps đa cluster]]: Kiểm chứng parameter filename và helm.valueFiles dùng .path.path, AppProject cho guestbook repo/namespace và labels prod/production theo version thực tế. [[sources/readme/argocd-cluster-manager]] status: open
- [ ] (2026-10-07) [[wiki/devops/Argo CD đa cluster]]: Tên fsel-premium/kpi-k8s-uat trong nguồn tương ứng hệ thống nào? Chưa có căn cứ đồng nhất với fsel-pt-teacher/kpi-uat. [[sources/readme/argocd-cluster-manager]] status: open
answer: kpi-k8s-uat tương ứng kpi-uat, sửa kpi-k8s-uat thành kpi-uat. fsel-premium là 1 context khác, nhưng chưa đi vào sử dụng
- [ ] (2026-10-07) [[wiki/devops/Kubeconfig ServiceAccount cho FPT FKE]]: CA trong Secret SA có khớp TLS API endpoint FKE bên ngoài không? Kiểm tra credential, TTL và trust thực tế trước dùng. [[sources/readme/Create_ServiceAccount_Kubeconfig]] status: open
answer: có
- [ ] (2026-10-07) [[wiki/devops/Dashboard capacity và requests pool prod3]]: Snapshot 12 node được đo ngày nào, pool prod3 hiện còn cùng scope không, dashboard JSON đã triển khai chưa? [[sources/readme/prod2-prod3-node-metrics-dashboard-plan]] status: open
answer: bỏ source và wiki này khỏi brain
- [ ] (2026-10-07) [[wiki/devops/Kafka OffsetOutOfRange trong Sentry]]: Nguồn diễn giải retention.bytes khoảng 500 MB cho topic; cần xác minh phạm vi topic/partition trước tính capacity cho 4 partition. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]] status: open
answer: cái này linh hoạt cho mỗi lần check lỗi
- [ ] (2026-10-07) [[wiki/devops/Relay buffer đầy và HTTP 503]]: Case Sentry được đo ngày nào và hiện đã khắc phục Relay 503/drop chưa? Chưa có input rate, envelope size và bằng chứng bottleneck dependency. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]] status: open
answer: đã xử lý được, closed
- [ ] (2026-10-07) [[wiki/devops/Triển khai và khám lỗi Submariner]]: Chốt version Submariner/Kubernetes/CNI/kube-proxy và kiểm chứng IPVS compatibility, driver ports/flags, Lighthouse behavior trước production. [[sources/readme/submarine multi-cluster]] status: open
answer: hỏi lại khi t cần triển khai, hiện tại chưa triển khai submariner
- [ ] (2026-10-07) [[wiki/devops/Kiến trúc Submariner đa VPC]]: Xác nhận FPT subnet L3/UDP hai chiều, NAT/source IP, underlay encryption, gateway candidates và API Broker reachable; prefix /14,/16 có được FKE chấp nhận? [[sources/readme/submarine multi-cluster]] status: open
answer: hỏi lại khi t cần triển khai, hiện tại chưa triển khai submariner
