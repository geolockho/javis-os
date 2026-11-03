# Bậc 2 - mTLS giữa gc và sc

Đoạn gc -> sc được mã hoá VÀ hai bên xác thực nhau bằng cert do CA nội bộ ký.
sc chỉ phục vụ client có cert hợp lệ (tức là gc), kể cả khi ai đó lọt vào mạng private.

## Nâng từ bậc 1 lên bậc 2 cần thêm gì

| Cluster | Thêm / đổi |
|---|---|
| gc | Certificate client `edge-client` (gc/02) -> Secret `edge-client-mtls` (tls.crt + tls.key + ca.crt); Ingress đổi `proxy-ssl-secret` sang `edge/edge-client-mtls` (gc/04) |
| sc | Secret `edge-client-ca` chỉ chứa ca.crt; Ingress thêm `auth-tls-secret`, `auth-tls-verify-client: on` (sc/04) |

Service internal, EndpointSlice, Certificate server, ConfigMap: giữ nguyên như bậc 1.

## Thứ tự apply (giả định đã ở bậc 1)

```bash
# 1. gc: cấp cert client trước, để sc bật verify xong là gc đã có cert gửi ngay
kubectl --context=gc apply -f gc/02-certificate-edge-client.yaml
kubectl --context=gc -n edge get certificate edge-client        # READY = True
kubectl --context=gc apply -f gc/04-ingress-api.yaml

# 2. sc
kubectl --context=sc -n app create secret generic edge-client-ca --from-file=ca.crt=../bac-1/shared/ca.crt
kubectl --context=sc apply -f sc/04-ingress-api.yaml
```

Nếu làm từ đầu (bỏ qua bậc 1): chạy đủ các bước trong `shared/README.md`.

## Kiểm tra

```bash
# không có client cert -> sc phải từ chối
kubectl --context=gc -n edge run t --rm -it --image=curlimages/curl -- \
  curl -si --resolve api.example.com:443:10.20.0.50 -k https://api.example.com/healthz
# mong đợi 400 "No required SSL certificate was sent"

# qua gc (có client cert) -> 200
curl -si https://api.example.com/healthz
```
