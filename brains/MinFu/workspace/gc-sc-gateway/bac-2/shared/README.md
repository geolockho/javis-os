# CA nội bộ dùng chung cho gc và sc

Tạo CA MỘT LẦN bằng openssl, rồi tạo Secret `internal-ca` giống hệt ở cả hai cluster.
cert-manager ở mỗi cluster dùng Secret này qua ClusterIssuer `internal-ca`.

```bash
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
  -keyout ca.key -out ca.crt -days 3650 -subj "/CN=internal-gateway-ca"

for ctx in gc sc; do
  kubectl --context=$ctx -n cert-manager create secret tls internal-ca --cert=ca.crt --key=ca.key
  kubectl --context=$ctx apply -f shared/clusterissuer-internal-ca.yaml
done

# CA (chỉ public) cho sc xác thực client cert của gc
kubectl --context=sc -n app create secret generic edge-client-ca --from-file=ca.crt
```

Thứ tự apply:

1. `shared/` ở cả 2 cluster (lệnh trên).
2. `kubectl --context=sc apply -f sc/`
3. Lấy IP internal LB: `kubectl --context=sc -n ingress-nginx get svc ingress-nginx-internal`
4. Điền IP đó vào `gc/01-service-endpointslice-sc.yaml`, rồi `kubectl --context=gc apply -f gc/`

Kiểm tra nhanh từ gc:

```bash
kubectl --context=gc -n edge run t --rm -it --image=curlimages/curl -- \
  curl -sv --resolve api.example.com:443:10.20.0.50 https://api.example.com/healthz --cacert /dev/null -k
# mong đợi 400 "No required SSL certificate was sent" = sc đã bắt đúng host và đang đòi mTLS
```
