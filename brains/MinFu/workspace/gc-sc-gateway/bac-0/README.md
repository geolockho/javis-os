# Bậc 0 - HTTP thường giữa gc và sc

Đoạn client -> gc vẫn HTTPS, cert public do bạn tự nạp vào Secret `edge/api-example-com-tls`. Đoạn gc -> sc đi HTTP thường qua kênh riêng / VPN.
Bảo vệ duy nhất ở sc là whitelist IP. Không cần cert-manager CA nội bộ, không cần cert gì thêm.

Dùng để: PoC, kiểm tra đường mạng, routing theo host và log/trace đã thông chưa.

## Thứ tự apply

```bash
# 1. sc
kubectl --context=sc apply -f sc/
kubectl --context=sc -n ingress-nginx get svc ingress-nginx-internal   # lấy EXTERNAL-IP (IP private)

# 2. điền IP đó vào gc/01-service-endpointslice-sc.yaml rồi
kubectl --context=gc apply -f gc/
```

## Kiểm tra

```bash
# từ một pod trên gc, gọi thẳng IP internal LB của sc với đúng Host
kubectl --context=gc -n edge run t --rm -it --image=curlimages/curl -- \
  curl -si -H "Host: api.example.com" http://10.20.0.50/healthz
# 200 = sc bắt đúng host. 404 = host ở sc không khớp. timeout = đường mạng / firewall.

# từ ngoài Internet
curl -si https://api.example.com/healthz
```

Đọc log gc (JSON): `up_connect` cao hoặc `-` = lỗi kênh / LB; `up_status` 5xx = lỗi ở sc, tra tiếp bằng `req_id`.

## Các TODO phải điền

- Annotation internal LB của ncc trong `sc/01`.
- `whitelist-source-range` (sc/03) và `proxy-real-ip-cidr` (sc/02): dải IP sc THỰC SỰ nhìn thấy từ gc. Lần đầu bỏ whitelist, gọi thử, đọc trường `client` trong log sc rồi mới điền.
- IP internal LB trong `gc/01`.
- `namespace: app`, tên Service, port backend.
- Secret `edge/api-example-com-tls` (cert public của host) phải có sẵn trên gc trước khi apply Ingress edge.
