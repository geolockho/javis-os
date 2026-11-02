---
superseded_by: yeu-cau-thong-ke-tai-nguyen-fsel-prod-2026-11-02
type: business
provenance: user
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
source: chat 2026-10-28 (39f6d62e)
---
Ngày 2026-10-28 người dùng yêu cầu việc định kỳ cho context/namespace fsel-prod: thống kê CPU/RAM request và usage 2 tiếng một lần gửi Slack, tổng kết cuối ngày, và đề xuất chỉnh HPA target, request/limit, min replicas. [[conversations/2026-10-28]]

Người dùng đã chốt (15:18 ngày 2026-10-28): [[conversations/2026-10-28]]
- Node: chỉ `node_role=appnodes-prod2`.
- Nguồn số liệu: Prometheus `https://prometheus-prod.fsel.edu.vn` (không cần auth, giữ 90 ngày).
- Repo ArgoCD để đối chiếu values: `D:\argocd-deploy-clean\values\fsel-prod`.
- Tin 2 tiếng là text, các thông số theo ảnh Grafana (Nodes, Total CPU/RAM, CPU/RAM Request %, Usage %).
- Muốn dùng năng lực của Javis (skill, agent, lịch).

Javis đã dựng ngày 2026-10-28:
- Skill `bao-cao-tai-nguyen-k8s-prometheus`, script `scripts/resource_report.py` (snapshot/daily) và `references/quy-tac-de-xuat.md`.
- Agent `tl-toi-uu-tai-nguyen-k8s`.
- Lịch `r_69ec7eedc3` (cron `0 */2 * * *`) và `r_d37073068f` (cron `30 23 * * *`), mức full, gửi Slack `C0C8RMMB7AN`.
- Quy tắc đề xuất là mặc định của Javis, người dùng chưa phản đối nhưng cũng chưa duyệt từng điểm: request = p95 7 ngày × 1.3, RAM request không thấp hơn đỉnh, có HPA thì p95 dưới 85% target, limit = đỉnh × 1.5, min replicas ≥ 2 cho service phục vụ người dùng.
- Chưa chạy thử qua lịch và chưa có tin nào gửi lên Slack (thực tế tính đến 15:30 ngày 2026-10-28). Lần chạy đầu theo lịch là 16:00 ngày 2026-10-28.

Phát hiện khi dựng (thực tế tính đến 2026-10-28): Prometheus scrape 2 bản kube-state-metrics nên phải lọc `service="monitoring-prometheus-kube-state-metrics"`; phần lớn HPA fsel-prod tạo bằng `kubectl autoscale`/Lens, không có trong git; `templates/` của repo ArgoCD chứa ConfigMap có mật khẩu DB dạng plaintext.

Thay cho loop cũ [[loop-monitor-cpu-ram-fsel-prod-da-dung]] (file loop đã bị xoá khỏi thư mục).

**Vì sao:** người dùng muốn theo dõi và tối ưu tài nguyên fsel-prod đều đặn. **Áp dụng:** khi được hỏi về báo cáo này, kiểm `javis_schedule op=list` và tin trên Slack để xác nhận lịch đã chạy; sửa quy tắc đề xuất trong file references của skill.


## Lịch sử
- [2026-11-02] Bị thay thế bởi [[yeu-cau-thong-ke-tai-nguyen-fsel-prod-2026-11-02]] (user đổi thông tin).
