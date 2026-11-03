---
name: Báo cáo tài nguyên K8s qua Prometheus
description: Thống kê CPU/RAM request/usage của node pool và service K8s từ Prometheus, gửi Slack, đề xuất chỉnh request/limit/HPA.
group: DevOps
---

## Khi nào dùng
- Lịch 2 tiếng hoặc cuối ngày gọi tới: "chạy báo cáo tài nguyên fsel-prod", "tổng kết tài nguyên cuối ngày".
- Người dùng hỏi: "fsel-prod đang dùng bao nhiêu % CPU/RAM", "service nào vượt request", "nên giảm request service nào", "HPA lmsapi có hợp lý không".
- Mặc định là cụm fsel-prod: Prometheus `https://prometheus-prod.fsel.edu.vn`, namespace `fsel-prod`, node `node_role=appnodes-prod2`. Cụm khác thì truyền `--prom`, `--ns`, `--node-role`.

## Chuẩn bị
- Python 3 trên máy chạy Javis (chỉ dùng stdlib). Prometheus không cần đăng nhập.
- Slack: tool `slack__slack_send_message` (qua `javis_run_tool` nếu không hiện trực tiếp). Kênh nhận: `C0C8RMMB7AN` (Minh Phú Space). Chỉ gửi Slack, không gửi Zalo.
- Repo ArgoCD: `D:\argocd-deploy-clean\values\fsel-prod\<thư-mục>\values.yaml` (chỉ dùng khi đề xuất).

## Cách chạy
Script: `scripts/resource_report.py` (đường dẫn đầy đủ `D:\javis-os\brains\MinFu\skills\bao-cao-tai-nguyen-k8s-prometheus\scripts\resource_report.py`).

```
python -I <script> snapshot              # cửa sổ 2 giờ gần nhất
python -I <script> daily                 # từ 00:00 hôm nay tới bây giờ + gợi ý thô trên 7 ngày
python -I <script> daily --date 2026-10-27
python -I <script> proposals             # chỉ bảng đề xuất (service dưới 50% request, số 7 ngày)
```
- stdout là tin nhắn đã định dạng sẵn cho Slack (dưới 5000 ký tự). Gửi NGUYÊN VĂN, không tự tính lại hay sửa số.
- Bảng service mặc định là bảng markdown (`|`), Slack vẽ thành bảng thật với cỡ chữ tin nhắn thường, to hơn code block một cỡ (người dùng yêu cầu 2026-10-28). Thêm `--table code` để quay về bảng chữ đều trong code block như bản cũ.
- Bảng xếp tăng dần theo trung bình %CPU và %RAM (dùng/request): service request nhiều mà ít dùng nằm trên đầu, service vượt request nằm cuối. Quá giới hạn Slack thì script tự ẩn bớt các dòng cuối và ghi rõ số service bị ẩn.
- `daily` in thêm dòng `===DE_XUAT===`, sau đó là bảng đề xuất (gửi thành reply trong thread), rồi dòng cuối `DATA_JSON: <path>`. Bỏ hai dòng đánh dấu đó ra trước khi gửi Slack.
- Bảng đề xuất gồm các service có p95 mỗi pod trong 7 ngày dưới 50% request: CPU/RAM request mới, target HPA mới, thư mục values cần sửa và HPA có nằm ngoài git không. Công thức nằm ở `references/quy-tac-de-xuat.md` mục 0. File JSON chứa từng service: `today`, `last_7d` (p95/max mỗi pod, số replica thấp nhất/cao nhất), `hpa`, `baseline` (gợi ý thô).
- Mỗi lần `snapshot` ghi thêm một dòng vào `workspace/k8s-resource-report/snapshots-YYYY-MM-DD.jsonl`.

## Quy trình
### Tin 2 tiếng (snapshot)
1. Chạy `snapshot`.
2. Gửi stdout nguyên văn vào `C0C8RMMB7AN`. Không kèm đề xuất.
3. Script lỗi (exit khác 0, timeout, HTTP lỗi): gửi một tin ngắn `fsel-prod báo cáo 2h LỖI: <dòng lỗi cuối>` vào cùng kênh.

### Tổng kết cuối ngày (daily)
1. Chạy `daily`. Gửi phần thống kê (trước `===DE_XUAT===`) vào `C0C8RMMB7AN`, giữ lại `ts` của tin vừa gửi.
2. Gửi bảng đề xuất (giữa `===DE_XUAT===` và `DATA_JSON`) nguyên văn thành reply trong thread đó.
3. Đọc file JSON và `references/quy-tac-de-xuat.md`, chỉ lập phần bổ sung theo mục 6 (nhóm Tăng, min/max replicas), gửi thành reply thứ hai nếu có.
4. Với mỗi service sắp đề xuất, mở `values.yaml` tương ứng (tìm theo `fullnameOverride`) để lấy giá trị đang khai báo và đường key cần sửa. Chỉ đọc `values.yaml`, KHÔNG mở thư mục `templates/`: các ConfigMap ở đó có mật khẩu DB dạng plaintext.
5. Không lấy được `ts` thì gửi các phần thành tin riêng theo đúng thứ tự.

## Bẫy
- Prometheus scrape 2 bản kube-state-metrics (Helm và Lens). Script đã lọc `service="monitoring-prometheus-kube-state-metrics"`; viết PromQL tay mà quên lọc thì số request bị nhân đôi.
- `kube_node_labels` không có label `node_role`. Danh sách node lấy từ cadvisor (`container_memory_working_set_bytes{id="/",node_role=...}`).
- Đừng escape tên node bằng `re.escape`: chuỗi PromQL không nhận `\-` và trả HTTP 400.
- `replicas_max` đếm số pod có số liệu tại mỗi mốc 5 phút, nên lúc rolling update (pod cũ và mới cùng chạy) số này cao hơn replica thật. Đừng dựa vào nó để kết luận HPA đã scale.
- Phần lớn HPA trong fsel-prod được tạo bằng `kubectl autoscale` hoặc Lens, không nằm trong git (`values.yaml` ghi `autoscaling.enabled: false`). Đề xuất HPA phải nói rõ sửa ở cụm hay ở values.
- `baseline` trong JSON chỉ là gợi ý thô theo công thức, không tự hiểu đặc thù từng service. Agent phải duyệt lại trước khi gửi.
- Không đổi khoá sắp xếp sang "% thấp hơn giữa CPU và RAM": gần như service nào CPU cũng dưới 5%, nên service đang vượt RAM (vd 109%) bị đẩy lên đầu bảng, sai ý "request nhiều mà ít dùng".
- `values_index` tìm thư mục values theo `fullnameOverride` và đọc `autoscaling.enabled` ngay dưới dòng `autoscaling:`. Đổi cấu trúc values.yaml thì cột "sửa ở" có thể ra "ngoài repo".
- Sàn 50m làm nhiều service có % p95 mới rất thấp (3-20%). Đó là sàn, không phải lỗi tính.
- Service có CPU dưới 1m thì cột dùng hiện `0m`, nghĩa là gần như không dùng chứ không phải mất số liệu.

## Kiểm chứng
- Thực tế tính đến 2026-10-28, số node trong tin khớp dashboard Grafana: 2 node, 109.1 cores, 218.2 GiB, CPU request khoảng 58%, RAM request khoảng 68%.
- Tuyệt đối không tự apply, không commit, không `kubectl patch`. Skill này chỉ đọc và đề xuất.
