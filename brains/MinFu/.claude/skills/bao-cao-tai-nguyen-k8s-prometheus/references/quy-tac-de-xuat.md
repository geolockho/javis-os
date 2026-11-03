# Quy tắc đề xuất tối ưu tài nguyên (request/limit/HPA)

Đầu vào: file `daily-YYYY-MM-DD.json` do `resource_report.py daily` sinh ra. Dùng số `last_7d` để đề xuất; số `today` chỉ để đối chiếu.
Mọi con số trong đề xuất phải lấy từ JSON hoặc `values.yaml`, không ước lượng.

## 1. Request
- CPU request mỗi pod = p95 CPU mỗi pod trong 7 ngày × 1.3, sàn 50m.
- RAM request mỗi pod = max(p95 × 1.3, đỉnh RAM thật của pod), sàn 128Mi. RAM không nén được, đặt dưới đỉnh thì dễ bị evict khi node thiếu RAM.
- Có HPA thì p95 / request mới phải dưới 85% target của HPA. Nếu không, HPA sẽ scale liên tục.
- Chỉ đề xuất khi lệch quá 20% so với hiện tại và lệch tối thiểu 50m CPU hoặc 128Mi RAM.

## 2. Limit
- CPU limit ≥ đỉnh CPU mỗi pod × 1.5 và ≥ request.
- RAM limit ≥ đỉnh RAM mỗi pod × 1.5 và ≥ request. KHÔNG đề xuất hạ RAM limit xuống dưới mức này (rủi ro OOMKilled).
- Pod đang chạm limit (đỉnh ≥ 90% limit) thì đưa vào nhóm "Tăng".

## 3. HPA
- `minReplicas`: service phục vụ người dùng (api, web, gateway, auth...) giữ tối thiểu 2 để có HA. Service đang min 1 mà phục vụ người dùng thì đề xuất lên 2. Min cao hơn 2 mà cả 7 ngày replica không vượt min và p95 dưới 50% target thì có thể hạ min, nhưng ghi "cân nhắc giờ cao điểm".
- `maxReplicas` 100 không thực tế với 2 node: ghi trần thực tế theo dung lượng (allocatable của node pool chia cho request mỗi pod, trừ phần đã request), đề xuất trần hợp lý nếu chênh lệch lớn.
- Target RAM: app .NET/JVM thường giữ RAM sau khi tăng, nên HPA theo RAM dễ scale lên mà không scale xuống. Service nào có target RAM và replica cao nhất vượt min thì nêu khả năng này, ghi "(cần xác minh)", gợi ý bỏ metric RAM hoặc nâng target. Không kết luận chắc nếu chưa thấy bằng chứng.
- Nhớ là đổi request cũng làm đổi % utilization mà HPA thấy. Luôn ghi p95 utilization mới theo request đề xuất (`util_p95_*_new`).

## 4. Chỗ sửa
- Request/limit: `D:\argocd-deploy-clean\values\fsel-prod\<thư-mục>\values.yaml`, key `fsel.resources.requests.cpu|memory`, `fsel.resources.limits.cpu|memory`. Tìm thư mục bằng `fullnameOverride` trùng tên service.
- HPA: nếu `fsel.autoscaling.enabled: true` thì sửa `fsel.autoscaling.*` trong values. Nếu `false` thì HPA đang được quản lý ngoài git (`kubectl autoscale`/Lens): ghi "sửa trực tiếp HPA trên cụm" kèm lệnh `kubectl --context fsel-prod -n fsel-prod patch hpa <tên> ...` để người dùng tự chạy, và nhắc nên đưa HPA vào git.
- Không tìm thấy thư mục values thì ghi "không có trong repo ArgoCD".

## 0. Phần script tự tính (từ 2026-10-29)
- Service có p95 mỗi pod trong 7 ngày dưới 50% request (CPU hoặc RAM) được script tính sẵn thành bảng đề xuất giảm request và nâng target HPA (`resource_report.py daily`, phần sau dòng `===DE_XUAT===`; hoặc chạy riêng `resource_report.py proposals`). Gửi bảng đó nguyên văn, không tính lại.
- Công thức script dùng: request mới = p95 × 1.3 (RAM không dưới đỉnh thật của pod), sàn 50m / 128Mi; có HPA thì p95 / request mới phải dưới 85% target. Target CPU dưới 70% (RAM dưới 80%) thì đề xuất nâng lên 70% (80%), chỉ khi nhờ vậy request giảm thêm được. Chỉ đề xuất khi giảm quá 20% và tối thiểu 50m / 128Mi. Limit giữ nguyên.
- Lý do: ngày 2026-10-28 agent tự ước lượng số đề xuất, ghi tổng RAM 9.0 GiB trong khi ước tính trước đó là 9.2 GiB. Số do script tính thì không lệch kiểu này.

## 5. Chọn lọc và trình bày
- Tối đa 10 đề xuất mỗi ngày, xếp theo lượng tài nguyên thay đổi (core, GiB). Chia 3 nhóm: **Tăng (rủi ro)** trước, rồi **Giảm (tiết kiệm)**, rồi **HPA**.
- Dòng đầu: tổng CPU/RAM request được giải phóng hoặc cần thêm, và % request của node pool sau khi áp dụng hết.
- Mỗi đề xuất 1-2 dòng: `service: CPU req 2000m → 400m (p95 7 ngày 198m/pod, HPA cpu 60% → p95 mới 51%) | values/fsel-prod/lmsapi/values.yaml fsel.resources.requests.cpu`.
- Dòng cuối: `_Chỉ là đề xuất, chưa áp dụng gì lên cụm hay repo._`
- Không có gì đáng đề xuất thì gửi một dòng: "Hôm nay không có đề xuất mới, tài nguyên nằm trong ngưỡng."
- Không dùng ký tự em dash.

## 6. Phần agent bổ sung sau bảng của script
- Chỉ nêu những gì script không tính: nhóm **Tăng (rủi ro)** (p95 hoặc đỉnh sát/vượt request, chạm limit) và `minReplicas`/`maxReplicas` theo mục 3. Tối đa 5 dòng.
- Không lặp lại service đã có trong bảng của script. Mọi số chép từ JSON, không ước lượng.
