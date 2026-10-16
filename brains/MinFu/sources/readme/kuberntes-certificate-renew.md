---
type: source
source_kind: own-note
status: processed
created: 2026-10-07
processed_at: 2026-10-07
wiki_links: ["[[wiki/devops/Quản lý kubeconfig nhiều cluster]]", "[[wiki/devops/Gia hạn certificate kubeconfig bằng kubeadm]]"]
url: null
original_path: "D:\\private01\\readme\\kuberntes-certificate-renew.md"
original_sha256: 27c1c6052e22e32f7150a74af1bf813bbf1bc12cd0fcda4c1c873830621148db
---

# Kiểm tra và renew kubeconfig certificate của Kubernetes

## Mục tiêu

Quy trình này thực hiện:

1. Xác định `~/.kube/config` đang dùng certificate từ:
   - `/etc/kubernetes/admin.conf`
   - `/etc/kubernetes/super-admin.conf`
   - Hay một certificate khác.
2. Kiểm tra thời hạn certificate.
3. Renew certificate bằng `kubeadm`.
4. Backup và copy certificate mới vào `~/.kube/config`.
5. Kiểm tra lại fingerprint, thời hạn và kết nối Kubernetes API.

---

## 1. Phân biệt admin.conf và super-admin.conf

| Kubeconfig | Certificate Subject | Quyền |
|---|---|---|
| `admin.conf` | `O=kubeadm:cluster-admins, CN=kubernetes-admin` | `cluster-admin` thông qua RBAC |
| `super-admin.conf` | `O=system:masters, CN=kubernetes-super-admin` | Bypass RBAC, chỉ dùng cho break-glass |
| `~/.kube/config` | Phụ thuộc file đã được copy vào | Cần kiểm tra |

`super-admin.conf` không nên dùng làm kubeconfig vận hành hằng ngày.

---

## 2. Xác định kubeconfig đang được sử dụng

Kiểm tra biến `KUBECONFIG`:

```bash
printf 'KUBECONFIG=%s\n' "${KUBECONFIG:-<not-set>}"
```

Kiểm tra context hiện tại:

```bash
kubectl config current-context
```

Nếu `KUBECONFIG` không được khai báo, `kubectl` mặc định sử dụng:

```text
~/.kube/config
```

Các bước bên dưới kiểm tra trực tiếp file `~/.kube/config`, không phụ thuộc biến `KUBECONFIG`.

---

## 3. Kiểm tra Subject và hạn certificate trong ~/.kube/config

```bash
kubectl config view \
  --kubeconfig ~/.kube/config \
  --raw \
  --minify \
  -o jsonpath='{.users[0].user.client-certificate-data}' |
base64 -d |
openssl x509 \
  -noout \
  -subject \
  -issuer \
  -serial \
  -dates \
  -fingerprint \
  -sha256
```

Nếu là `admin.conf`, kết quả Subject sẽ tương tự:

```text
subject=O = kubeadm:cluster-admins, CN = kubernetes-admin
```

Nếu là `super-admin.conf`, kết quả Subject sẽ tương tự:

```text
subject=O = system:masters, CN = kubernetes-super-admin
```

Ý nghĩa thời gian:

```text
notBefore = thời điểm certificate bắt đầu có hiệu lực
notAfter  = thời điểm certificate hết hạn
```

Nếu lệnh báo:

```text
Could not read certificate
```

kiểm tra phương thức xác thực của kubeconfig:

```bash
kubectl config view \
  --kubeconfig ~/.kube/config \
  --raw \
  --minify
```

Kubeconfig có thể đang sử dụng:

- `client-certificate-data`
- Đường dẫn `client-certificate`
- Token
- Exec credential plugin

Quy trình này áp dụng trực tiếp cho kubeconfig dùng `client-certificate-data`.

---

## 4. So sánh fingerprint để xác định file nguồn

Chạy toàn bộ đoạn sau:

```bash
CURRENT_KUBECONFIG="${HOME}/.kube/config"

get_client_cert_fingerprint() {
  kubectl config view \
    --kubeconfig "$1" \
    --raw \
    --minify \
    -o jsonpath='{.users[0].user.client-certificate-data}' |
  base64 -d |
  openssl x509 -noout -fingerprint -sha256 2>/dev/null
}

CURRENT_FP="$(get_client_cert_fingerprint "$CURRENT_KUBECONFIG")"
ADMIN_FP="$(get_client_cert_fingerprint /etc/kubernetes/admin.conf)"

if [ -f /etc/kubernetes/super-admin.conf ]; then
  SUPER_ADMIN_FP="$(get_client_cert_fingerprint /etc/kubernetes/super-admin.conf)"
else
  SUPER_ADMIN_FP="<file-not-found>"
fi

printf 'CURRENT     : %s\n' "$CURRENT_FP"
printf 'ADMIN       : %s\n' "$ADMIN_FP"
printf 'SUPER-ADMIN : %s\n' "$SUPER_ADMIN_FP"

if [ -z "$CURRENT_FP" ]; then
  echo "RESULT: Không đọc được client-certificate-data từ ~/.kube/config"
elif [ "$CURRENT_FP" = "$ADMIN_FP" ]; then
  echo "RESULT: ~/.kube/config đang dùng certificate từ admin.conf"
elif [ "$CURRENT_FP" = "$SUPER_ADMIN_FP" ]; then
  echo "RESULT: ~/.kube/config đang dùng certificate từ super-admin.conf"
else
  echo "RESULT: ~/.kube/config đang dùng certificate khác"
fi
```

Kết quả mong đợi:

```text
RESULT: ~/.kube/config đang dùng certificate từ admin.conf
```

Fingerprint là cách kiểm tra chính xác hơn việc chỉ nhìn `Subject`, vì certificate được renew vẫn có thể giữ nguyên Subject nhưng có serial number và fingerprint khác.

---

## 5. Kiểm tra hạn toàn bộ certificate của kubeadm

Chạy trên control-plane node:

```bash
sudo kubeadm certs check-expiration
```

Các certificate quan trọng:

```text
admin.conf
super-admin.conf
apiserver
apiserver-etcd-client
apiserver-kubelet-client
controller-manager.conf
scheduler.conf
```

Các CA:

```text
ca
etcd-ca
front-proxy-ca
```

Lệnh này kiểm tra certificate trong `/etc/kubernetes`, không khẳng định bản `~/.kube/config` đã được cập nhật.

---

## 6. Kiểm tra certificate có hết hạn trong 30 ngày không

```bash
kubectl config view \
  --kubeconfig ~/.kube/config \
  --raw \
  --minify \
  -o jsonpath='{.users[0].user.client-certificate-data}' |
base64 -d |
openssl x509 -checkend 2592000 -noout
```

Kết quả:

```text
Certificate will not expire
```

Nghĩa là certificate còn hạn trên 30 ngày.

Nếu kết quả:

```text
Certificate will expire
```

certificate sẽ hết hạn trong vòng 30 ngày hoặc đã hết hạn.

---

## 7. Renew admin.conf

Renew certificate trong file gốc:

```bash
sudo kubeadm certs renew admin.conf
```

Kết quả mong đợi:

```text
certificate embedded in the kubeconfig file for the admin to use and for kubeadm itself renewed
```

Kiểm tra certificate mới trong `/etc/kubernetes/admin.conf`:

```bash
sudo kubectl config view \
  --kubeconfig /etc/kubernetes/admin.conf \
  --raw \
  --minify \
  -o jsonpath='{.users[0].user.client-certificate-data}' |
base64 -d |
openssl x509 \
  -noout \
  -subject \
  -issuer \
  -serial \
  -dates \
  -fingerprint \
  -sha256
```

---

## 8. Backup kubeconfig hiện tại

```bash
mkdir -p ~/.kube

cp -a \
  ~/.kube/config \
  ~/.kube/config.backup-"$(date +%Y%m%d-%H%M%S)"
```

Kiểm tra file backup:

```bash
ls -lh ~/.kube/config*
```

---

## 9. Copy admin.conf mới vào ~/.kube/config

```bash
sudo cp /etc/kubernetes/admin.conf ~/.kube/config

sudo chown "$(id -u):$(id -g)" ~/.kube/config

chmod 600 ~/.kube/config
```

Lưu ý: thao tác này thay toàn bộ nội dung `~/.kube/config`.

Nếu file đang chứa nhiều cluster/context đã merge, không copy đè trực tiếp. Cần renew hoặc cập nhật riêng `client-certificate-data` của context tương ứng.

---

## 10. Kiểm tra Subject và hạn sau khi copy

```bash
kubectl config view \
  --kubeconfig ~/.kube/config \
  --raw \
  --minify \
  -o jsonpath='{.users[0].user.client-certificate-data}' |
base64 -d |
openssl x509 \
  -noout \
  -subject \
  -issuer \
  -serial \
  -dates \
  -fingerprint \
  -sha256
```

Kết quả phải có Subject:

```text
subject=O = kubeadm:cluster-admins, CN = kubernetes-admin
```

Và `notAfter` phải là thời hạn mới.

---

## 11. So sánh fingerprint sau khi copy

```bash
CURRENT_FP="$(
  kubectl config view \
    --kubeconfig ~/.kube/config \
    --raw \
    --minify \
    -o jsonpath='{.users[0].user.client-certificate-data}' |
  base64 -d |
  openssl x509 -noout -fingerprint -sha256
)"

ADMIN_FP="$(
  sudo kubectl config view \
    --kubeconfig /etc/kubernetes/admin.conf \
    --raw \
    --minify \
    -o jsonpath='{.users[0].user.client-certificate-data}' |
  base64 -d |
  openssl x509 -noout -fingerprint -sha256
)"

printf 'CURRENT: %s\n' "$CURRENT_FP"
printf 'ADMIN  : %s\n' "$ADMIN_FP"

if [ "$CURRENT_FP" = "$ADMIN_FP" ]; then
  echo "VERIFY: PASS - ~/.kube/config đã dùng admin.conf mới"
else
  echo "VERIFY: FAIL - fingerprint không khớp"
fi
```

Kết quả đúng:

```text
VERIFY: PASS - ~/.kube/config đã dùng admin.conf mới
```

---

## 12. Kiểm tra user hiện tại

```bash
kubectl auth whoami
```

Kết quả dự kiến:

```text
ATTRIBUTE   VALUE
Username    kubernetes-admin
Groups      [kubeadm:cluster-admins system:authenticated]
```

Kiểm tra quyền:

```bash
kubectl auth can-i '*' '*' --all-namespaces
```

Kết quả:

```text
yes
```

---

## 13. Kiểm tra kết nối Kubernetes API

```bash
kubectl get --raw='/readyz?verbose'
```

Kiểm tra node:

```bash
kubectl get nodes -o wide
```

Kiểm tra namespace:

```bash
kubectl get namespaces
```

Nếu các lệnh trả kết quả bình thường, kubeconfig mới hoạt động.

---

## 14. Quy trình rút gọn

```bash
# 1. Kiểm tra certificate hiện tại
kubectl config view \
  --kubeconfig ~/.kube/config \
  --raw \
  --minify \
  -o jsonpath='{.users[0].user.client-certificate-data}' |
base64 -d |
openssl x509 -noout -subject -issuer -dates -fingerprint -sha256

# 2. Kiểm tra toàn bộ certificate
sudo kubeadm certs check-expiration

# 3. Backup kubeconfig
cp -a \
  ~/.kube/config \
  ~/.kube/config.backup-"$(date +%Y%m%d-%H%M%S)"

# 4. Renew admin.conf
sudo kubeadm certs renew admin.conf

# 5. Copy admin.conf mới
sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chown "$(id -u):$(id -g)" ~/.kube/config
chmod 600 ~/.kube/config

# 6. Kiểm tra certificate sau khi copy
kubectl config view \
  --kubeconfig ~/.kube/config \
  --raw \
  --minify \
  -o jsonpath='{.users[0].user.client-certificate-data}' |
base64 -d |
openssl x509 -noout -subject -issuer -dates -fingerprint -sha256

# 7. Kiểm tra kết nối
kubectl auth whoami
kubectl get --raw='/readyz?verbose'
kubectl get nodes -o wide
```

---

## 15. Trường hợp ~/.kube/config đang dùng super-admin.conf

Nếu kết quả kiểm tra là:

```text
CN = kubernetes-super-admin
O = system:masters
```

Khuyến nghị chuyển sang `admin.conf`:

```bash
sudo kubeadm certs renew admin.conf

cp -a \
  ~/.kube/config \
  ~/.kube/config.super-admin.backup-"$(date +%Y%m%d-%H%M%S)"

sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chown "$(id -u):$(id -g)" ~/.kube/config
chmod 600 ~/.kube/config
```

Sau đó kiểm tra:

```bash
kubectl auth whoami
kubectl auth can-i '*' '*' --all-namespaces
kubectl get nodes
```

Chỉ khi có yêu cầu duy trì `super-admin.conf` cho mục đích break-glass mới renew:

```bash
sudo kubeadm certs renew super-admin.conf
```

Không nên dùng `super-admin.conf` làm kubeconfig vận hành hằng ngày.

---

## 16. Trường hợp dùng KUBECONFIG khác

Nếu đang cấu hình:

```bash
export KUBECONFIG=/path/to/cluster.yaml
```

thì `kubectl` sử dụng `/path/to/cluster.yaml`, không sử dụng `~/.kube/config`.

Kiểm tra:

```bash
printf '%s\n' "$KUBECONFIG"
```

Sau khi renew, cần cập nhật đúng file đang sử dụng:

```bash
sudo cp /etc/kubernetes/admin.conf /path/to/cluster.yaml
sudo chown "$(id -u):$(id -g)" /path/to/cluster.yaml
chmod 600 /path/to/cluster.yaml
```

---

## 17. Lưu ý cho cluster HA

Đối với cluster có nhiều control-plane node:

- `kubeadm certs renew` chỉ renew certificate trên node đang chạy lệnh.
- Nếu renew toàn bộ control-plane certificate, phải thực hiện lần lượt trên từng control-plane node.
- Không thực hiện đồng thời trên tất cả node.
- Sau `kubeadm certs renew all`, cần restart các static Pod control plane lần lượt để nạp certificate mới.
- Riêng việc renew và copy `admin.conf` không yêu cầu restart API Server.

---

## Nguồn tham khảo

- [Kubernetes – Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
- [Kubernetes – Certificate Management with kubeadm](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/)
- [Kubernetes – PKI certificates and requirements](https://kubernetes.io/docs/setup/best-practices/certificates/)