# Bậc 1 - TLS một chiều giữa gc và sc

Đoạn gc -> sc được mã hoá. gc verify cert server của sc bằng CA nội bộ. sc vẫn chỉ nhận diện gc qua whitelist IP.
Cần cert-manager ở sc (cấp cert server) và một CA nội bộ dùng chung.

## Nâng từ bậc 0 lên bậc 1 cần thêm gì

| Cluster | Thêm / đổi |
|---|---|
| cả 2 | Secret `cert-manager/internal-ca` + ClusterIssuer `internal-ca` (shared/) |
| sc | Service internal mở cổng 443 (sc/01), Certificate server (sc/03), Ingress có khối `tls` (sc/04) |
| gc | EndpointSlice trỏ cổng 443 (gc/01), Secret `sc-ca` chỉ chứa ca.crt (gc/02), Ingress backend HTTPS + proxy-ssl-verify (gc/04) |

ConfigMap hai bên không đổi.

## Thứ tự apply

```bash
# 0. tạo CA một lần
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
  -keyout shared/ca.key -out shared/ca.crt -days 3650 -subj "/CN=internal-gateway-ca"

# 1. CA + issuer ở cả hai cluster (gc chỉ cần ca.crt, nhưng nạp đủ để sau lên bậc 2 khỏi làm lại)
for ctx in gc sc; do
  kubectl --context=$ctx -n cert-manager create secret tls internal-ca --cert=shared/ca.crt --key=shared/ca.key
  kubectl --context=$ctx apply -f shared/clusterissuer-internal-ca.yaml
done

# 2. sc
kubectl --context=sc apply -f sc/
kubectl --context=sc -n app get certificate api-example-com-internal      # READY = True
kubectl --context=sc -n ingress-nginx get svc ingress-nginx-internal      # lấy IP private

# 3. gc
kubectl --context=gc -n edge create secret generic sc-ca --from-file=ca.crt=shared/ca.crt
# điền IP internal LB vào gc/01 rồi
kubectl --context=gc apply -f gc/
```

## Kiểm tra

```bash
kubectl --context=gc -n edge run t --rm -it --image=curlimages/curl -- \
  curl -si --resolve api.example.com:443:10.20.0.50 --cacert /dev/null -k https://api.example.com/healthz
# 200 = TLS phiên 2 bắt tay được và sc route đúng host.
# Nếu gc trả 502 với log "upstream SSL certificate verify error": SAN cert sc không khớp proxy-ssl-name, hoặc CA sai.
```

Giữ `shared/ca.key` ở nơi an toàn (vault, không commit). Mất key là phải cấp lại toàn bộ cert.
