# Wiki Log

Time-ordered log (append-only). Each entry: `## [YYYY-MM-DD] kind | title` (kind: init/ingest/update/query/lint/migrate).

## [2026-10-07] ingest | argocd-cluster-manager

- Nguồn: [[sources/readme/argocd-cluster-manager]], nhập từ D:/private01/readme; nội dung gốc giữ nguyên, đối chiếu SHA-256.
- Trang tạo/liên quan: [[wiki/devops/Argo CD đa cluster]], [[wiki/devops/Quản lý kubeconfig nhiều cluster]], [[wiki/devops/Phân quyền và credential Argo CD]], [[wiki/devops/ApplicationSet và GitOps đa cluster]], [[wiki/devops/Lighthouse và service discovery đa cluster]].

### Ý chính và insight

- Mục tiêu: Argo CD trung tâm quản lý API nhiều cluster, credential runtime qua SA/Cluster Secret. [[sources/readme/argocd-cluster-manager]]
- Runbook: kiểm tra kubeconfig, đăng ký cluster, gắn label, giới hạn AppProject, generate và verify Application đúng target. [[sources/readme/argocd-cluster-manager]]
- Mẫu Git files/Cluster/Matrix và destination từ values; Root Application/Webhook hỗ trợ GitOps. [[sources/readme/argocd-cluster-manager]]
- Cần giữ rõ khác biệt project default, nhãn Directory nhưng YAML files, labels prod/production, tên context và valueFiles chưa kiểm chứng. [[sources/readme/argocd-cluster-manager]]

- Phạm vi: chưng cất tài liệu; không thực thi lệnh can thiệp hệ thống, không tạo task tự động.

## [2026-10-07] ingest | Create_ServiceAccount_Kubeconfig

- Nguồn: [[sources/readme/Create_ServiceAccount_Kubeconfig]], nhập từ D:/private01/readme; nội dung gốc giữ nguyên, đối chiếu SHA-256.
- Trang tạo/liên quan: [[wiki/devops/Kubeconfig ServiceAccount cho FPT FKE]].

### Ý chính và insight

- Mục tiêu: bootstrap token kubeconfig từ credential portal FKE còn hiệu lực, giảm phụ thuộc certificate client ngắn hạn. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
- Runbook SA/RBAC/manual token Secret/CA/API endpoint, dựng file riêng và kiểm chứng sau khi certificate cũ hết hạn. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
- Tách quyền theo consumer; phân biệt TokenRequest có hạn với Secret token, rotate/revoke và kiểm tra auth/TLS. [[sources/readme/Create_ServiceAccount_Kubeconfig]]
- Mẫu thời hạn 24 giờ và CA từ Secret không thay kiểm tra credential/API endpoint thực tế. [[sources/readme/Create_ServiceAccount_Kubeconfig]]

- Phạm vi: chưng cất tài liệu; không thực thi lệnh can thiệp hệ thống, không tạo task tự động.

## [2026-10-07] ingest | kuberntes-certificate-renew

- Nguồn: [[sources/readme/kuberntes-certificate-renew]], nhập từ D:/private01/readme; nội dung gốc giữ nguyên, đối chiếu SHA-256.
- Trang tạo/liên quan: [[wiki/devops/Quản lý kubeconfig nhiều cluster]], [[wiki/devops/Gia hạn certificate kubeconfig bằng kubeadm]].

### Ý chính và insight

- Phân biệt admin.conf và super-admin.conf bằng Subject và SHA-256 fingerprint, kiểm tra đúng KUBECONFIG/phương thức auth. [[sources/readme/kuberntes-certificate-renew]]
- Runbook backup, renew admin.conf, cập nhật credential bản dùng rồi verify thời hạn/fingerprint/identity/quyền/API. [[sources/readme/kuberntes-certificate-renew]]
- Không copy đè kubeconfig multi-context; HA renew từng control-plane, tách renew admin.conf khỏi renew all/static Pod restart. [[sources/readme/kuberntes-certificate-renew]]

- Phạm vi: chưng cất tài liệu; không thực thi lệnh can thiệp hệ thống, không tạo task tự động.

## [2026-10-07] ingest | prod2-prod3-node-metrics-dashboard-plan

- Nguồn: [[sources/readme/prod2-prod3-node-metrics-dashboard-plan]], nhập từ D:/private01/readme; nội dung gốc giữ nguyên, đối chiếu SHA-256.
- Trang tạo/liên quan: [[wiki/devops/Dashboard capacity và requests pool prod3]].

### Ý chính và insight

- Kế hoạch Grafana capacity/requests pool appnodes-prod3, không phải realtime usage hoặc dashboard đã triển khai. [[sources/readme/prod2-prod3-node-metrics-dashboard-plan]]
- Correction: pool appnodes-prod3 nhưng node_role appnodes-prod2; PromQL lọc theo pool label. [[sources/readme/prod2-prod3-node-metrics-dashboard-plan]]
- Nguồn ghi snapshot 12 node, allocatable và requests; thiếu ngày đo nên không coi là dữ liệu live. [[sources/readme/prod2-prod3-node-metrics-dashboard-plan]]
- Mục tiêu JSON, DS_PROMETHEUS, stats/bảng theo node và test plan import/đối chiếu totals. [[sources/readme/prod2-prod3-node-metrics-dashboard-plan]]

- Phạm vi: chưng cất tài liệu; không thực thi lệnh can thiệp hệ thống, không tạo task tự động.

## [2026-10-07] ingest | sentry-self-hosted-ingest-troubleshooting

- Nguồn: [[sources/readme/sentry-self-hosted-ingest-troubleshooting]], nhập từ D:/private01/readme; nội dung gốc giữ nguyên, đối chiếu SHA-256.
- Trang tạo/liên quan: [[wiki/devops/Chẩn đoán pipeline ingest Sentry]], [[wiki/devops/Kafka OffsetOutOfRange trong Sentry]], [[wiki/devops/Tăng throughput consumer Sentry]], [[wiki/devops/Relay buffer đầy và HTTP 503]].

### Ý chính và insight

- Case Sentry 24.1.0: tách lỗi trước Kafka, consumer và downstream; lag 0 có thể do producer không ghi mới. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- Nguồn ghi reset riêng ingest-events về latest sau dừng mọi member; earliest/latest khác nhau về backlog và mất dữ liệu. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- Nguồn ghi tăng 1 lên 4 partition/process giúp consumer; buffer Relay tăng 1000 lên 10000 vẫn đầy và 503/drop chưa xử lý xong. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]
- Kế hoạch đo request/project/envelope size/Redis/Kafka/disk trước scale Relay; snapshot và đơn vị retention cần xác minh. [[sources/readme/sentry-self-hosted-ingest-troubleshooting]]

- Phạm vi: chưng cất tài liệu; không thực thi lệnh can thiệp hệ thống, không tạo task tự động.

## [2026-10-07] ingest | submarine multi-cluster

- Nguồn: [[sources/readme/submarine multi-cluster]], nhập từ D:/private01/readme; nội dung gốc giữ nguyên, đối chiếu SHA-256.
- Trang tạo/liên quan: [[wiki/devops/Kiến trúc Submariner đa VPC]], [[wiki/devops/CIDR và Globalnet cho Submariner]], [[wiki/devops/Triển khai và khám lỗi Submariner]], [[wiki/devops/Lighthouse và service discovery đa cluster]], [[wiki/devops/Đo latency và MTU của Submariner]].

### Ý chính và insight

- Thiết kế Submariner ngày 2026-08-12: Broker metadata riêng data plane, gateway ở subnet FPT có route private. [[sources/readme/submarine multi-cluster]]
- CIDR không overlap ưu tiên non-Globalnet; prefix ví dụ cần FPT xác nhận; gateway active/passive không chia tải active-active. [[sources/readme/submarine multi-cluster]]
- Kế hoạch requirements/deploy/join/verify, Lighthouse ServiceExport/Import và DNS clusterset.local. [[sources/readme/submarine multi-cluster]]
- Phương pháp đo underlay/Pod/simple HTTP/real API, gateway CPU/NIC và MTU/MSS; không có benchmark live. [[sources/readme/submarine multi-cluster]]
- Compatibility IPVS/CNI, driver/ports, NAT và underlay encryption cần đối chiếu version pin trước production. [[sources/readme/submarine multi-cluster]]

- Phạm vi: chưng cất tài liệu; không thực thi lệnh can thiệp hệ thống, không tạo task tự động.

## [2026-10-07] ingest | Kiểm tra độ phủ bộ readme

- Đã lưu 6 source và tạo 16 trang wiki, cập nhật index và 10 câu hỏi/nhóm vấn đề cần xác minh.
- Câu 1: Thêm target Argo CD và chứng minh deploy đúng cluster bằng cách nào? Được bao phủ bởi [[Argo CD đa cluster]], [[Quản lý kubeconfig nhiều cluster]], [[Phân quyền và credential Argo CD]], [[ApplicationSet và GitOps đa cluster]].
- Câu 2: FKE credential và kubeadm certificate khác gì, rotate/renew/revoke ra sao? Được bao phủ bởi [[Kubeconfig ServiceAccount cho FPT FKE]], [[Gia hạn certificate kubeconfig bằng kubeadm]].
- Câu 3: Dashboard chọn đúng pool và đo request hay usage? Được bao phủ bởi [[Dashboard capacity và requests pool prod3]].
- Câu 4: Vì sao Kafka lag 0 mà ingest vẫn lỗi, reset earliest/latest khác gì? Được bao phủ bởi [[Chẩn đoán pipeline ingest Sentry]], [[Kafka OffsetOutOfRange trong Sentry]], [[Tăng throughput consumer Sentry]], [[Relay buffer đầy và HTTP 503]].
- Câu 5: Submariner cần route/CIDR/Broker/discovery gì và isolate latency ra sao? Được bao phủ bởi [[Kiến trúc Submariner đa VPC]], [[CIDR và Globalnet cho Submariner]], [[Triển khai và khám lỗi Submariner]], [[Lighthouse và service discovery đa cluster]], [[Đo latency và MTU của Submariner]].

## [2026-10-07] update | Câu trả lời của người dùng và gỡ dashboard

- Nguồn: [[sources/readme/open-questions-answers-2026-10-07]]; giữ nguyên nội dung file Telegram.
- Cập nhật 13 trang: [[wiki/devops/Phân quyền và credential Argo CD]], [[wiki/devops/ApplicationSet và GitOps đa cluster]], [[wiki/devops/Argo CD đa cluster]], [[wiki/devops/Kubeconfig ServiceAccount cho FPT FKE]], [[wiki/devops/Chẩn đoán pipeline ingest Sentry]], [[wiki/devops/Kafka OffsetOutOfRange trong Sentry]], [[wiki/devops/Tăng throughput consumer Sentry]], [[wiki/devops/Relay buffer đầy và HTTP 503]], [[wiki/devops/Kiến trúc Submariner đa VPC]], [[wiki/devops/CIDR và Globalnet cho Submariner]], [[wiki/devops/Triển khai và khám lỗi Submariner]], [[wiki/devops/Lighthouse và service discovery đa cluster]], [[wiki/devops/Đo latency và MTU của Submariner]].
- Chốt project Argo CD, git.files và tên context; CA FKE có xác nhận người dùng. [[sources/readme/open-questions-answers-2026-10-07]]
- Case Sentry closed; Submariner chưa triển khai và điều kiện chỉ hỏi lại khi cần. [[sources/readme/open-questions-answers-2026-10-07]]
- Câu hỏi readme: 6 resolved/removed, 3 deferred, 1 chưa có câu trả lời vẫn open. [[sources/readme/open-questions-answers-2026-10-07]]
- Theo yêu cầu, gỡ `sources/readme/prod2-prod3-node-metrics-dashboard-plan.md` và `wiki/devops/Dashboard capacity và requests pool prod3.md` khỏi brain; giữ file gốc `D:/private01/readme/prod2-prod3-node-metrics-dashboard-plan.md`. [[sources/readme/open-questions-answers-2026-10-07]]
- Các liên kết dashboard trong nhật ký ingest cũ và file câu trả lời gốc chỉ còn là dấu vết lịch sử; không sửa nội dung nguồn hoặc log append-only.

## [2026-10-07] ingest | tự học từ chat

Đã tạo:
- [[GitLab Runner dùng Docker executor]]
## [2026-10-07] cập nhật | Cache build image với Docker và Buildah

Chưng cất trao đổi về cache của Docker builder trên host và Buildah trong job tạm thành [[wiki/devops/Cache build image với Docker và Buildah]]. Ghi rõ phương án Buildah đang được đánh giá, chưa có quyết định chuyển; đối chiếu theo snapshot CI local và tài liệu chính thức.

## [2026-10-08] ingest | tự học từ chat

Đã tạo:
- [[devops/Vertical Pod Autoscaler (VPA)]]

## [2026-10-13] ingest | tự học từ chat

Đã tạo:
- [[Lỗi No scopes requested khi cài Slack app]]

## [2026-10-23] ingest | tự học từ chat

Đã tạo:
- [[Cấp kubeconfig theo namespace có duyệt admin]]

## [2026-10-26] ingest | tự học từ chat

Đã tạo:
- [[Cookie secret của oauth2-proxy phải đúng 16, 24 hoặc 32 byte]]

## [2026-10-27] ingest | tự học từ chat

Đã tạo:
- [[Gọi API xuyên cluster qua gateway HTTPS mTLS]]

## [2026-11-01] ingest | tự học từ chat

Đã tạo:
- [[Điều khiển và hỗ trợ lái trên VinFast VF 6]]

## [2026-11-05] ingest | tự học từ chat

Đã tạo:
- [[Đổi tên Facebook Page]]

## [2026-11-10] ingest | tự học từ chat

Đã tạo:
- [[Solution .NET (.sln)]]

## [2026-11-10] ingest | tự học từ chat

Đã tạo:
- [[Stage .pre trong GitLab CI/CD]]

## [2026-11-10] ingest | tự học từ chat

Đã tạo:
- [[Lưu trữ bền vững của SonarQube trên Kubernetes]]

## [2026-11-10] ingest | tự học từ chat

Đã tạo:
- [[Ephemeral storage của container Kubernetes]]

## [2026-11-10] ingest | tự học từ chat

Đã tạo:
- [[ephemeral-storage trong Kubernetes]]

## [2026-11-10] ingest | tự học từ chat

Đã tạo:
- [[Chọn SonarQube Community Build hay Developer Edition]]

## [2026-11-11] ingest | tự học từ chat

Đã tạo:
- [[Ước lượng resource request theo pod nặng nhất và pod cũ nhất]]
