# kubeconfig-generator

Web nhỏ cấp kubeconfig **read-only theo namespace** cho dev, trên 2 cluster `fsel-prod` (FKE 1.25) và `fsel-local` (1.34).

Dev đăng nhập SSO GitLab, chọn namespace đang mở, admin duyệt, dev bấm tải. **Namespace được mở bằng label** `kubeconfig-generator/enabled=true` do admin gắn tay; Kyverno tự sinh RoleBinding cho tool theo label đó, không phải sửa ConfigMap hay chạy script. **Quyền xin không phụ thuộc group GitLab:** ai đăng nhập được cũng thấy cùng danh sách, admin duyệt từng request. ServiceAccount, RoleBinding (tới ClusterRole `view`) và token **chỉ được tạo lúc dev tải**, token có hạn (TokenRequest), không lưu kubeconfig.

## Kiến trúc

```
Dev ──HTTPS──> Ingress ──> Service :80 ──> Pod
                                           ├─ oauth2-proxy :4180  (SSO GitLab, gắn X-Forwarded-Email)
                                           └─ app 127.0.0.1:8000 (FastAPI, 1 worker)
                                                ├─ PostgreSQL (request, link, audit)
                                                ├─ API server fsel-prod  (kubeconfig SA tool)
                                                └─ API server fsel-local (kubeconfig SA tool)
```

- **App chỉ nghe 127.0.0.1**, nên mọi request phải đi qua oauth2-proxy trong cùng pod. Từ ngoài không gửi thẳng header danh tính giả được.
- **1 replica, 1 worker** (`strategy: Recreate`). Rate limit và job dọn dẹp chạy trong bộ nhớ. Job dọn dẹp vẫn giữ `pg_try_advisory_lock` để lỡ chạy 2 bản cũng không xử lý trùng.
- **PostgreSQL** với psycopg 3 + SQL thuần. App tự chạy `migrations/*.sql` lúc khởi động.
- **`kubernetes` client**, mỗi cluster một `ApiClient`.

| Thư mục | Nội dung |
|---|---|
| `app/` | `main.py` (route), `service.py` (nghiệp vụ), `k8s.py`, `cleanup.py`, `catalog.py`, `auth.py`, `db.py`, `ratelimit.py`, `slack.py`, `logging_redact.py`, `templates/` |
| `migrations/` | Schema SQL |
| `deploy/` | Deployment, Service, Ingress, NetworkPolicy, Secret mẫu, `rbac/tool.yaml` (RBAC của tool, chung 2 cluster), `kyverno/` (policy sinh RoleBinding theo label và bảo vệ label) |
| `scripts/` | `make_tool_kubeconfig.sh` |
| `tests/` | Test unit, test luồng với PostgreSQL, test trên cluster thật |

## Cài đặt

### 1. PostgreSQL
Tạo database và user riêng (dùng Postgres có sẵn):
```sql
CREATE USER kubeconfig_generator WITH PASSWORD '...';
CREATE DATABASE kubeconfig_generator OWNER kubeconfig_generator;
```
App tự tạo bảng lúc khởi động. Muốn chạy tay: `psql "$DATABASE_URL" -f migrations/001_init.sql`.

### 2. Kyverno, RBAC cho tool, policy (mỗi cluster)
Cả hai cluster cần Kyverno (đã cài ở namespace `kube-public`, release `kyverno`: fsel-prod v1.11.5, fsel-local v1.19.2):
- **fsel-prod (K8s 1.25):** Kyverno **1.11.x** (Helm chart `kyverno` 3.1.x). Bản mới hơn không hỗ trợ 1.25.
- **fsel-local (K8s 1.34):** bản Kyverno có hỗ trợ 1.34 theo bảng tương thích của Kyverno.

Policy trong `deploy/kyverno/` chỉ dùng trường có từ 1.11, nên dùng chung cho cả hai.

SA của tool nằm ở `kube-public` (namespace có sẵn, manifest không tạo namespace để `kubectl delete -f` không xoá namespace dùng chung). App vẫn chạy ở `fsel-internal-tools`: pod không dùng SA của chính nó mà gọi cluster bằng token trong Secret `kubeconfig-generator-clusters`. Tên `kube-public` chứa `kube` nên app và Kyverno đều chặn, tool không tự cấp token trong namespace chứa SA của mình.

```bash
for ctx in fsel-prod fsel-local; do
  kubectl --context $ctx apply -f deploy/rbac/tool.yaml
  kubectl --context $ctx apply -f deploy/kyverno/          # 00 RBAC cho Kyverno, 10 generate, 20 bảo vệ label
done
mkdir -p secrets
./scripts/make_tool_kubeconfig.sh fsel-prod  fsel-prod  > secrets/fsel-prod.yaml
./scripts/make_tool_kubeconfig.sh fsel-local fsel-local > secrets/fsel-local.yaml
```
`secrets/` đã nằm trong `.gitignore`. RBAC của tool **không đổi khi mở thêm namespace**, chỉ apply một lần.

Kiểm tra sau khi apply:
```bash
kubectl --context fsel-local get clusterpolicy kubeconfig-generator-issuer-rolebinding kubeconfig-generator-protect-namespace-labels
kubectl --context fsel-local label ns <ns-test> kubeconfig-generator/enabled=true
kubectl --context fsel-local -n <ns-test> get rolebinding kubeconfig-generator-issuer       # phải có
kubectl --context fsel-local auth can-i create serviceaccounts/token -n <ns-test> \
  --as=system:serviceaccount:kube-public:kubeconfig-generator                                  # yes
kubectl --context fsel-local auth can-i create serviceaccounts/token -n kube-system \
  --as=system:serviceaccount:kube-public:kubeconfig-generator                                  # no
```

Quyền của tool (`deploy/rbac/tool.yaml`):

| Quyền | Phạm vi | Vì sao |
|---|---|---|
| `serviceaccounts`: get, list, create, delete | Chỉ namespace có label (RoleBinding do Kyverno sinh) | Tạo/xoá SA cho dev |
| `serviceaccounts/token`: create | Như trên | Sinh token bằng TokenRequest |
| `rolebindings`: get, list, create, delete | Như trên | Gắn SA vào ClusterRole `view` |
| `clusterroles`: bind, `resourceNames: [view]` | Như trên | Xem dưới |
| `namespaces`: get, list | Toàn cluster | Kiểm tra tồn tại, đọc label để dựng danh sách namespace mở |

- **Vì sao cần `bind`:** K8s chặn tạo RoleBinding tới một role mà người tạo không tự có đủ quyền của role đó (chống leo thang quyền). Tool không có quyền của `view`, nên phải có `bind`, và chỉ trên đúng ClusterRole `view`.
- **Vì sao RoleBinding theo từng namespace, không dùng ClusterRoleBinding:** quyền `create serviceaccounts/token` ở mức cluster cho phép sinh token của **bất kỳ** SA nào, kể cả SA admin trong `kube-system`. Gắn theo namespace thì tool chỉ làm được việc đó ở namespace admin đã mở.
- Tool không có quyền tạo Role, ClusterRole, ClusterRoleBinding, cũng không sửa được namespace (không gắn label được).

Kyverno (`deploy/kyverno/`):

| File | Việc |
|---|---|
| `00-kyverno-rbac.yaml` | Gộp thêm quyền cho background controller của Kyverno: quản RoleBinding, `bind` đúng ClusterRole `kubeconfig-generator-issuer` |
| `10-generate-issuer-rolebinding.yaml` | Namespace có label `true` hoặc `draining` thì sinh RoleBinding `kubeconfig-generator-issuer` cho SA tool. `synchronize: true` (gỡ label là RoleBinding mất, sửa tay là bị dựng lại), `generateExisting: true` (áp cả namespace có sẵn). Loại cứng `*kube*`, `cd`, `haproxy`, `rabbitmq`, `redis`, `kyverno`, `argocd`, `fsel-internal-tools` |
| `20-protect-namespace-labels.yaml` | Chỉ `cluster-admin` được sửa label/annotation của tool; label chỉ nhận `true`/`draining`; không gỡ thẳng từ `true` (phải qua `draining`) |

**Cần lưu ý:** tool tạo được token cho **mọi** SA trong namespace được mở, không chỉ SA nó tạo. Vì vậy chỉ mở namespace của ứng dụng, đừng mở namespace có SA quyền cao (operator, CI runner, controller). Namespace loại cứng ở trên đã tính tới việc này.

### 3. OAuth app trên GitLab
Tạo ở Group, Settings, Applications (hoặc Admin, Applications):
- **Redirect URI:** `https://kubeconfig-generator.fsel.edu.vn/oauth2/callback`
- **Confidential:** bật. **Scopes:** `openid`, `profile`, `email`.
- Chép Application ID và Secret (Secret chỉ hiện một lần).

### 4. Secret
```bash
kubectl -n fsel-internal-tools create secret generic kubeconfig-generator-oauth2 \
  --from-literal=client-id=... --from-literal=client-secret=... \
  --from-literal=cookie-secret="$(openssl rand -base64 32 | tr -- '+/' '-_')"
kubectl -n fsel-internal-tools create secret generic kubeconfig-generator-clusters \
  --from-file=fsel-prod.yaml=secrets/fsel-prod.yaml --from-file=fsel-local.yaml=secrets/fsel-local.yaml
kubectl -n fsel-internal-tools create secret generic kubeconfig-generator-env --from-env-file=.env
```
Mẫu biến ở `.env.example`, mẫu Secret ở `deploy/secret.example.yaml`. Không commit `.env`, kubeconfig hay token.

### 5. Image và deploy
Push lên `main` thì GitLab CI (`.gitlab-ci.yml`, runner tag `docker-runner`) tự build và push image `$CI_REGISTRY_IMAGE:main-<short-sha>-<ddmmyy>`. Build tay khi cần:
```bash
docker build -t <REGISTRY>/other-services/kubeconfig-generator:0.1.0 .
docker push <REGISTRY>/other-services/kubeconfig-generator:0.1.0
```
Sửa các chỗ `TODO` trong `deploy/` (registry, `ingressClassName`, nhãn namespace của ingress controller, địa chỉ Postgres trong NetworkPolicy), rồi khai báo thư mục `deploy/` (trừ `secret.example.yaml`) trong ArgoCD. `deploy/rbac/` và `deploy/kyverno/` phải apply lên **cả hai** cluster, còn Deployment chỉ chạy trên fsel-local.

## Cấu hình

Toàn bộ qua biến môi trường, xem `.env.example`. Các biến chính:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `DATABASE_URL` | (bắt buộc) | PostgreSQL |
| `PUBLIC_URL` | (bắt buộc) | Dùng để dựng link tải và kiểm tra Origin |
| `CLUSTERS`, `KUBECONFIG_<CLUSTER>` | `fsel-prod,fsel-local` | Kubeconfig của SA tool, mỗi cluster một file |
| `NAMESPACE_REFRESH` | `1m` | Cache danh sách namespace có label. Lúc duyệt và lúc tải luôn hỏi lại cluster. `NAMESPACES_PATH` cũ bị bỏ qua |
| `ADMIN_EMAILS` | `hophu@atlantic.edu.vn` | So khớp chính xác, không phân biệt hoa thường |
| `ALLOW_SELF_APPROVE` | `false` | Cho admin tự duyệt request của mình |
| `CLAIM_WINDOW` / `LINK_TTL` | `24h` / `15m` | Hạn nhận sau khi duyệt / hạn của mỗi link |
| `EXPIRATION_OPTIONS` / `MAX_EXPIRATION` | `1d,7d,30d,90d` / `90d` | Lựa chọn thời hạn cho dev (tối thiểu `10m`) |
| `ALLOWED_CLUSTER_ROLES` | `view` | Role được phép ở annotation `kubeconfig-generator/role`. Thêm role thì phải thêm vào `resourceNames` của `deploy/rbac/tool.yaml` |
| `FORBIDDEN_NAMESPACES` | (trống) | Thêm vào danh sách cấm cứng: `cd, haproxy, rabbitmq, redis, kyverno, argocd, fsel-internal-tools`, tên chứa `kube`. Nên thêm cả vào exclude của policy Kyverno |
| `CLIENT_IP_HEADER` | `X-Real-IP` | Header IP thật do ingress-nginx đặt |
| `RATE_LIMIT_PER_SECOND` | `3` | Theo IP, cho mọi route |
| `LINK_RATE_PER_MINUTE` / `DOWNLOAD_RATE_PER_MINUTE` | `10` / `10` | Theo email / theo IP |
| `INSTANCE_ID` | `default` | Đổi khi có 2 bản (vd staging) dùng chung cluster, để job dọn dẹp không đụng tài nguyên của nhau |

### Mở và đóng namespace bằng label
Admin cluster gắn tay, trên đúng cluster cần mở. Namespace phải có sẵn.

```bash
# Mở: dev thấy namespace trong vòng NAMESPACE_REFRESH (1 phút), Kyverno sinh RoleBinding cho tool
kubectl --context fsel-local label ns team-a kubeconfig-generator/enabled=true
# (tuỳ chọn) role khác view, phải nằm trong ALLOWED_CLUSTER_ROLES
kubectl --context fsel-local annotate ns team-a kubeconfig-generator/role=view

# Đóng, BẮT BUỘC qua 2 bước:
kubectl --context fsel-local label ns team-a kubeconfig-generator/enabled=draining --overwrite
#   đợi 1 lượt job dọn (<= 5 phút): kubeconfig đã cấp bị thu hồi, request đã duyệt chưa tải bị thu hồi,
#   request chờ duyệt bị từ chối. Kiểm ở /admin: không còn dòng "Đã cấp" nào ở namespace đó.
kubectl --context fsel-local label ns team-a kubeconfig-generator/enabled-
```

| Label `kubeconfig-generator/enabled` | Dev thấy, xin được | Admin duyệt được | Tool còn RoleBinding | Job dọn |
|---|---|---|---|---|
| `true` | Có | Có | Có | Quét tài nguyên mồ côi |
| `draining` | Không | Không | Có | Thu hồi mọi quyền đã cấp |
| (không có) | Không | Không | Không | Không đụng tới |

- **Vì sao phải qua `draining`:** gỡ label là Kyverno xoá RoleBinding của tool ngay. Khi đó tool không còn quyền xoá SA đã cấp, token của dev sống tới hết hạn. Policy `drain-before-disable` chặn gỡ thẳng từ `true`. Xoá hẳn namespace thì không bị chặn (SA và token mất theo).
- **Label là cổng cấp quyền.** Policy `only-admins-change` chỉ cho `cluster-admin` sửa label/annotation này. Tool không có quyền sửa namespace, nên kể cả tool bị chiếm cũng không tự mở được `kube-system`.
- App vẫn tự lọc namespace cấm (kể cả khi Kyverno lỡ sinh RoleBinding), kiểm lại lúc submit, lúc duyệt và ngay trước khi cấp. Lúc duyệt và lúc tải luôn hỏi lại cluster, không dùng cache.
- **Không có khái niệm group.** Ai đăng nhập SSO cũng thấy cùng danh sách, admin duyệt từng request. Header group từ oauth2-proxy (nếu có) bị bỏ qua.
- Đọc label lỗi (API server không trả lời): app giữ danh sách cũ, ghi log, và báo ở `/admin/debug/claims`.

### Kiểm tra header từ oauth2-proxy
Admin mở `https://kubeconfig-generator.fsel.edu.vn/admin/debug/claims`. Trang trả JSON gồm email nhận được, header `X-Forwarded-*` (đã bỏ token và cookie), IP thật, namespace đang mở (`catalog`), đang thu hồi (`draining`) và lỗi đọc label theo cluster (`catalog_errors`). Nếu email rỗng thì kiểm tra header rồi đặt `EMAIL_HEADER`.

## Cách dùng

**Dev**
1. Mở trang, chọn cluster, namespace (hiện mọi namespace đang mở bằng label, không lọc theo group), thời hạn, gửi.
2. Đợi trên trang (tự làm mới 5 giây một lần). Khi admin duyệt sẽ hiện nút **Tạo link tải**.
3. Bấm tạo link rồi mở link, bấm **Tải kubeconfig**. Link dùng một lần, hết hạn sau 15 phút, chỉ người xin mở được. Trong 24 giờ sau khi duyệt có thể tạo link mới nếu lỡ.
4. Dùng: `kubectl --kubeconfig kubeconfig-fsel-local-team-a.yaml get pods`.

Giới hạn: tối đa 5 request chờ duyệt, không xin trùng (cùng cluster, namespace) khi đang có request chờ duyệt hoặc kubeconfig còn hạn.

**Admin** (`/admin`, chỉ hiện với email trong `ADMIN_EMAILS`, mọi endpoint admin đều kiểm tra phía server)
- Duyệt, từ chối (kèm lý do), thu hồi. Có thông báo Slack khi có request mới.
- Danh sách kubeconfig đang hiệu lực, audit log ở `/admin/audit`.

## Kiểm tra giới hạn thời hạn token

API server có thể cắt ngắn thời hạn TokenRequest (cờ `--service-account-max-token-expiration`). Tool luôn lấy thời hạn thật từ `expirationTimestamp` trong phản hồi:
- Lưu vào cột `token_expires_at`, hiện cho dev trên trang và trong header `X-Token-Expires-At` của file tải.
- Nếu ngắn hơn mức xin quá 60 giây: header `X-Token-Truncated: true` và audit ghi "API server cắt ngắn thời hạn token".

Kiểm tra trước trên từng cluster, dùng một SA có sẵn quyền thấp (lệnh này không tạo object, nhưng vẫn là thao tác trên cluster):
```bash
kubectl --context fsel-prod -n <ns> create token <sa> --duration=2160h \
  | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | grep -o '"exp":[0-9]*'
```
So `exp` với thời điểm hiện tại: khoảng 90 ngày là không bị cắt. Không in và không lưu token ra file. Test `tests/cluster` `test_token_expiry_from_tokenrequest` cũng kiểm tra thời hạn thật trả về.

## Bảo mật

- **Token link tải nằm sau dấu `#`** (`/dl#<token>`). Trình duyệt không gửi phần này lên server, nên token không lọt vào access log của ingress-nginx, oauth2-proxy hay app. Trang `/dl` đọc token rồi gửi bằng POST. DB chỉ lưu SHA-256 của token.
- **Đánh dấu link đã dùng** bằng `UPDATE ... WHERE used_at IS NULL`, đồng thời chuyển request sang `issuing` trong cùng transaction. Bấm song song (cùng link hoặc nhiều link) chỉ tạo đúng 1 SA.
- **Tạo trên cluster lỗi:** xoá theo label `request-id`, trả link về chưa dùng, ghi audit. Job dọn dẹp quét lại tài nguyên mồ côi.
- **Xoá luôn chọn theo label** `app.kubernetes.io/managed-by=kubeconfig-generator` + `kubeconfig-generator/instance` + `kubeconfig-generator/request-id`, và kiểm lại label từng object trước khi xoá. Email nằm ở annotation, label chỉ chứa hash.
- **Log:** app không ghi token. Bộ lọc log còn che chuỗi dạng JWT, token link và webhook Slack. Access log của uvicorn tắt, app tự ghi access log không có query string. Response tải có `Cache-Control: no-store`.
- **CSRF:** cookie oauth2-proxy `SameSite=Lax` và app từ chối POST có `Origin` khác `PUBLIC_URL`.
- **Audit chỉ thêm:** trigger chặn UPDATE, DELETE, TRUNCATE trên `audit_log`.

## Test

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

pytest                                            # test unit; test cần DB/cluster tự bỏ qua

# Test luồng đầy đủ với PostgreSQL (schema public của DB này sẽ bị XOÁ)
docker run -d --rm --name kcg-test-pg -e POSTGRES_PASSWORD=test -p 127.0.0.1:55432:5432 postgres:16-alpine
TEST_DATABASE_URL=postgresql://postgres:test@127.0.0.1:55432/postgres pytest
docker stop kcg-test-pg

# Trên cluster thật (tạo SA/RoleBinding thật trong namespace test)
KCG_TEST_KUBECONFIG=secrets/fsel-local.yaml KCG_TEST_NS_A=<ns> KCG_TEST_NS_B=<ns khác> pytest -m cluster
pytest -m "cluster and slow"                      # chờ token 10 phút hết hạn
```

| Nghiệm thu | Test |
|---|---|
| Xin namespace A: get pods được ở A, Forbidden ở B | `tests/cluster` `test_get_pods_in_a_forbidden_in_b` |
| Token hết hạn thì không dùng được | `tests/cluster` `test_expired_token_rejected` (slow) |
| Revoke xong không dùng được nữa | `test_revoke_*`, `tests/cluster` `test_revoke_invalidates_token` |
| Không xin được namespace chưa gắn label, trong blacklist, kể cả sửa form | `test_tampered_form_rejected_and_nothing_created`, `test_parse_labeled_filters` |
| Gắn label là mở, `draining` là ngừng cấp mới và thu hồi hết, gỡ label là đóng | `test_new_label_opens_namespace`, `test_draining_*`, `test_approve_rejected_when_label_changed`, `test_download_blocked_when_drained_after_approve`, `test_cleanup_drains_namespace` |
| RBAC tool không có RoleBinding/Namespace; policy Kyverno loại cứng namespace cấm, đồng bộ RoleBinding | `test_tool_rbac_*`, `test_kyverno_*` |
| Không thuộc group nào vẫn xin được; header group không mở thêm quyền | `test_any_logged_in_user_can_request_without_group`, `test_group_header_is_ignored` |
| Từ chối hoặc đã duyệt chưa tải thì không có gì trên cluster | `test_rejected_request_creates_nothing`, `test_approved_but_not_downloaded_creates_nothing` |
| Token không xuất hiện trong log | `test_tokens_never_logged`, `test_redact_*` |
| Không phải admin gọi endpoint admin thì 403 | `test_non_admin_gets_403_on_admin_endpoints` |
| Admin không tự duyệt khi cờ tắt | `test_admin_cannot_self_approve` |
| Link dùng lần 2, quá 15 phút, người khác mở thì bị từ chối | `test_link_second_use_rejected`, `test_link_expired_rejected`, `test_link_opened_by_other_user_rejected` |
| Hai lần bấm song song chỉ tạo 1 SA | `test_parallel_clicks_same_link_create_one_sa`, `test_parallel_different_links_create_one_sa` |
| Lỗi giữa chừng không để lại SA/RoleBinding mồ côi | `test_cluster_failure_leaves_no_orphans_and_link_reusable` |
| Job dọn dẹp chỉ xoá tài nguyên có label của tool | `test_cleanup_only_deletes_tool_labelled_resources`, `tests/cluster` `test_delete_only_touches_labelled` |
