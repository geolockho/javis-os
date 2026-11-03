Hãy viết công cụ cấp kubeconfig read-only theo namespace cho dev.

## 1. Bối cảnh
- Cluster hỗ trợ: fsel-prod (FKE, K8s 1.25) và fsel-local (K8s 1.34).
- Triển khai tool ở fsel-local, chạy 1 replica. Tool dùng 2 kubeconfig admin riêng (mỗi cluster một ServiceAccount quyền tối thiểu), nạp qua .env.
- Server URL và CA trong kubeconfig dev cấp ra lấy từ kubeconfig admin của đúng cluster đó.
- Quy mô (số dev, số namespace): chưa ước tính. Không cần tối ưu tải.

## 2. Xác thực và phân quyền người dùng
- Dev đăng nhập SSO GitLab. Đặt web sau oauth2-proxy (hoặc OIDC trực tiếp). App chỉ tin danh tính từ proxy (email, groups), không tin dữ liệu form.
- App chỉ nhận request từ proxy (NetworkPolicy hoặc chỉ nghe nội bộ) để không giả mạo header được.
- Giới hạn IP ở ingress chỉ là lớp phụ, không thay xác thực.
- Admin: cấu hình trong .env là danh sách email (mặc định chỉ hophu@atlantic.edu.vn), so khớp chính xác, không phân biệt hoa thường. Chỉ admin mới thấy tính năng ẩn. Kiểm tra phía server cho MỌI endpoint admin, không chỉ ẩn nút.
- Admin không được duyệt request do chính mình tạo, trừ khi bật cờ `ALLOW_SELF_APPROVE=true` trong .env (mặc định false).
- Quyền xin KHÔNG phụ thuộc group GitLab (đổi ngày 2026-10-23, vì dev thường được add vào project chứ không phải ai cũng nằm trong group). Mọi người đăng nhập SSO thấy cùng một danh mục namespace {cluster: [namespace hoặc {namespace, role}]}, admin duyệt từng request. Danh mục vẫn là whitelist: không có trong danh mục thì từ chối. `role` mặc định `view`, chỉ chấp nhận giá trị nằm trong danh sách ClusterRole cho phép ở .env.
- Namespace bị cấm ngay cả khi có trong danh mục: cd, haproxy, rabbitmq, redis, và tên chứa `kube`.

## 3. Chức năng
### 3.1 Dev
- Form gồm: Email (lấy từ SSO, chỉ hiển thị), Cluster, Namespace, Expiration (vd: 1 month, tối đa 90 days).
- Namespace hiển thị theo cluster đã chọn và theo map nhóm của dev. Server kiểm tra lại map và blacklist khi submit, không tin giá trị form.
- Quyền duy nhất: read-only, dùng ClusterRole `view` có sẵn qua RoleBinding trong đúng namespace.
- Dev gửi yêu cầu thì request ở trạng thái "chờ duyệt". Chưa tạo gì trên cluster.
- Chống spam: mỗi dev tối đa 5 request đang chờ duyệt; không cho tạo request trùng (cùng dev, cluster, namespace) khi đã có request chờ duyệt hoặc kubeconfig còn hiệu lực.
- Dev đợi trên trang web (tự làm mới trạng thái). Khi admin duyệt, web hiện nút "Tạo link tải".
- Dev xem được danh sách request và kubeconfig của chính mình (trạng thái, ngày hết hạn).

### 3.2 Admin (tính năng ẩn)
- Xem danh sách request: ai xin, cluster, namespace, quyền, khi nào, hết hạn khi nào, trạng thái.
- Duyệt hoặc từ chối request (từ chối có thể kèm lý do). Gửi Slack khi có request mới (webhook trong .env; Slack lỗi thì chỉ log cảnh báo, không làm hỏng request).
- Liệt kê tất cả kubeconfig đã cấp và thu hồi (revoke).

### 3.3 Cấp phát và giao kubeconfig
Chốt: SA, RoleBinding và token chỉ được tạo trên cluster khi dev bấm tải link, không tạo lúc admin duyệt.

- Admin duyệt xong, request ở trạng thái "đã duyệt", có hạn nhận 24 giờ (cấu hình được). Trong hạn này dev có thể bấm "Tạo link tải" nhiều lần. Mỗi link: token ngẫu nhiên đủ dài, dùng một lần, TTL 15 phút, lưu hash trong DB. Quá hạn nhận mà chưa tải thì request hết hiệu lực, dev phải xin lại.
- Link chỉ dùng được khi người mở đã đăng nhập SSO và email khớp với người xin request. Người khác mở link thì từ chối.
- Khi dev mở link: đánh dấu link đã dùng một cách nguyên tử (UPDATE có điều kiện) để hai lần bấm song song chỉ một lần thành công. Sau đó:
  - Tạo ServiceAccount `dev-<user>-<rand>` trong namespace.
  - Gắn label: managed-by, requester, request-id.
  - Tạo RoleBinding tới ClusterRole `view`, cùng label. Không tạo Role, không tạo ClusterRole/ClusterRoleBinding.
  - Sinh token bằng TokenRequest API với thời hạn dev yêu cầu. Không dùng secret token vĩnh viễn.
  - Sinh kubeconfig có context trỏ vào namespace mặc định, trả về dạng file tải xuống. Không lưu kubeconfig.
- Nếu bước tạo trên cluster lỗi: dọn phần đã tạo (theo label request-id), trả link về trạng thái chưa dùng để dev thử lại trong TTL, ghi lỗi vào audit.
- Thời hạn token tính từ lúc tải. Thời hạn thực tế lấy từ `expirationTimestamp` trong phản hồi TokenRequest. Nếu API server cắt ngắn hơn mức dev xin (fsel-prod 1.25), hiển thị đúng thời hạn thực cho dev và ghi vào DB.
- README ghi rõ cách kiểm tra giới hạn này.

### 3.4 Revoke và dọn dẹp
- Revoke = xóa ServiceAccount + RoleBinding theo label request-id. Tuyệt đối không xóa theo tên hay xóa SA của người khác. Token gắn với SA nên xóa SA là vô hiệu token; viết test xác nhận.
- Revoke request chưa tải (chưa có gì trên cluster) thì chỉ đổi trạng thái trong DB.
- Job dọn dẹp chạy bằng thread trong app (chỉ 1 replica). Job xóa SA và RoleBinding đã hết hạn (cùng cách chọn theo label), đồng thời đánh dấu request/link hết hạn. Chạy lại một lượt khi app khởi động để bù lúc app tắt. Dùng `pg_advisory_lock` hoặc tương đương để lỡ chạy 2 bản cũng không xử lý trùng.
- Cập nhật trạng thái trong DB sau mỗi thao tác. Nếu xóa trên cluster lỗi thì giữ trạng thái "revoke lỗi" và job thử lại ở lượt sau.

## 4. Ràng buộc bảo mật
- Quyền tối thiểu cho dev: chỉ RoleBinding vào ClusterRole `view`.
- Không ghi token vào log (gồm cả token link tải và token SA). Không lưu kubeconfig sau khi giao. Response tải về có `Cache-Control: no-store`.
- Rate limit 3 request/giây theo IP, áp ở app. Lấy IP thật từ header của ingress đáng tin. Thêm giới hạn riêng cho endpoint tạo link và endpoint tải.
- Request bị từ chối hoặc vi phạm map/blacklist thì không tạo gì trên cluster.
- Audit log (ghi DB, chỉ thêm, không sửa/xóa qua app): ai xin (email từ SSO), cluster, namespace, quyền, khi nào, hết hạn khi nào, người duyệt, thời điểm tải, kết quả.
- RBAC của tool: xuất manifest tối thiểu cho mỗi cluster, gồm: tạo/xóa/liệt kê SA, tạo token (`serviceaccounts/token`), tạo/xóa/liệt kê RoleBinding, `get` namespace để kiểm tra tồn tại, và verb `bind` trên ClusterRole `view` (giới hạn bằng `resourceNames: [view]`). Giải thích vì sao cần `bind` (chống leo thang quyền khi tạo RoleBinding tới role mà tool không tự có). Không cấp quyền rộng hơn.

## 5. Kiến trúc và kỹ thuật
- Ngôn ngữ: Python. Thư viện: `kubernetes` client (nêu rõ nếu chọn thư viện khác).
- Web nhỏ, framework tùy bạn đề xuất.
- Lưu request, link và audit ở Postgres có sẵn. Không cần manifest cho DB. Cần file migration/schema SQL.
- Cấu hình bằng .env: Postgres, đường dẫn 2 kubeconfig admin, đường dẫn file map, danh sách email admin, Slack webhook, hạn nhận 24 giờ, TTL link 15 phút, các giá trị cần thiết khác.
- Health endpoint `/healthz` cho probe.

## 6. Đầu ra
- Cấu trúc thư mục và code đầy đủ.
- README: cài đặt, cấu hình, cách dùng, cách kiểm tra giới hạn thời hạn token.
- Dockerfile và manifest K8s cho service (Deployment 1 replica, Service, Ingress, NetworkPolicy, RBAC cho tool).
- File danh mục namespace mẫu (cluster -> namespace/role), không theo group.
- File .env mẫu.

## 7. Nghiệm thu (viết test cho từng case)
- Dev xin namespace A: `kubectl get pods` được ở A, Forbidden ở B.
- Token hết hạn thì không dùng được.
- Revoke xong thì dùng không được nữa.
- Dev không xin được namespace ngoài map hoặc trong blacklist (kể cả sửa giá trị form).
- Request bị từ chối thì không tạo gì trên cluster; request đã duyệt nhưng chưa tải cũng chưa có gì trên cluster.
- Token không xuất hiện trong log.
- Người không phải admin gọi endpoint admin thì bị 403.
- Admin không tự duyệt request của chính mình khi cờ tắt.
- Link tải dùng lần hai, sau 15 phút, hoặc mở bởi người khác thì bị từ chối.
- Hai lần bấm tải song song chỉ tạo đúng một SA.
- Tạo trên cluster lỗi giữa chừng thì không để lại SA/RoleBinding mồ côi.
- Job dọn dẹp chỉ xóa tài nguyên có label managed-by của tool.

## Cách làm
- Thiếu thông tin quan trọng thì hỏi tôi trước, đừng tự giả định.
- Đề xuất kiến trúc ngắn trước, chờ tôi duyệt rồi mới viết code.
