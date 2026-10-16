---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["kubeadm certs renew", "admin.conf", "super-admin.conf", "Kubeconfig certificate renewal"]
source: "[[sources/readme/kuberntes-certificate-renew]]"
---

# Gia hạn certificate kubeconfig bằng kubeadm

Runbook này áp dụng kubeconfig X.509 của cluster kubeadm, không mặc định dùng cho FKE token/exec credential. Nội dung là quy trình từ nguồn, chưa xác nhận certificate nào đang hết hạn. [[sources/readme/kuberntes-certificate-renew]]

## Nhận dạng đúng credential

Nguồn phân biệt admin.conf (`O=kubeadm:cluster-admins, CN=kubernetes-admin`) với super-admin.conf (`O=system:masters, CN=kubernetes-super-admin`); super-admin dùng break-glass/bypass RBAC, không dùng hằng ngày. Nhận dạng này cần đối chiếu version thực tế. [[sources/readme/kuberntes-certificate-renew]]

Kiểm tra KUBECONFIG/context và kiểu auth trước; decode trực tiếp dành cho client-certificate-data. Field rỗng có thể do certificate file, token hoặc exec plugin. Subject có thể không đổi sau renew, nên so SHA-256 fingerprint với admin.conf/super-admin.conf. [[sources/readme/kuberntes-certificate-renew]]

Lệnh trích metadata và kiểm tra hạn theo nguồn: [[sources/readme/kuberntes-certificate-renew]]

```bash
kubectl config view --kubeconfig ~/.kube/config --raw --minify -o jsonpath='{.users[0].user.client-certificate-data}' | base64 -d | openssl x509 -noout -subject -issuer -serial -dates -fingerprint -sha256
sudo kubeadm certs check-expiration
```

Check-expiration đọc `/etc/kubernetes`, không chứng minh bản local đã cập nhật. `openssl x509 -checkend 2592000 -noout` kiểm tra cửa sổ 30 ngày. [[sources/readme/kuberntes-certificate-renew]]

## Renew và verify (quy trình)

1. Backup file đang dùng, xác định đúng certificate và control-plane. [[sources/readme/kuberntes-certificate-renew]]
2. `sudo kubeadm certs renew admin.conf`, rồi kiểm tra notAfter/serial/fingerprint bản gốc mới. [[sources/readme/kuberntes-certificate-renew]]
3. Cập nhật đúng file/context/credential, ownership, permission 600; file multi-context không copy đè cả file. [[sources/readme/kuberntes-certificate-renew]]
4. So fingerprint bản dùng với bản renew, test `kubectl auth whoami`, `auth can-i`, `/readyz?verbose`, nodes/namespaces. Thành công của các bước là tiêu chí nghiệm thu, chưa thực thi trong ingest. [[sources/readme/kuberntes-certificate-renew]]

## HA và super-admin

Renew chỉ tác động node chạy lệnh; renew toàn control-plane cần làm lần lượt từng node. Nguồn phân biệt renew admin.conf không cần restart API server với renew all cần restart static Pods lần lượt để nạp certificate. Không suy hệ thống hiện có nhiều master từ phần HA. [[sources/readme/kuberntes-certificate-renew]]

Nếu đang dùng super-admin, nguồn khuyến nghị chuyển admin.conf cho vận hành; chỉ renew super-admin.conf khi cần credential break-glass. [[sources/readme/kuberntes-certificate-renew]]

Liên quan: [[Quản lý kubeconfig nhiều cluster]], [[Kubeconfig ServiceAccount cho FPT FKE]].
