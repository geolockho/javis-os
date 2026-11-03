# gc-sc-gateway - tách gateway cluster (gc) và service cluster (sc)

Cùng một kiến trúc, ba mức bảo mật trên đoạn gc -> sc. Mỗi thư mục tự đủ để apply.

```text
Client -> Cloudflare -> LB public gc -> [gc] ingress-nginx edge
                                              |  kênh riêng / VPN
                                              v
                          LB internal sc -> [sc] ingress-nginx -> Service -> Pod
```

| Thư mục | gc -> sc | sc nhận diện gc bằng | Cần cert nội bộ |
|---|---|---|---|
| `bac-0/` | HTTP thường | whitelist IP | không |
| `bac-1/` | HTTPS, gc verify sc | whitelist IP | cert server cho sc, ca.crt ở gc |
| `bac-2/` | mTLS, hai bên verify nhau | client cert + whitelist IP | thêm cert client cho gc |

Lộ trình: PoC ở `bac-0`, lên `bac-1` khi có cert-manager + CA nội bộ, lên `bac-2` trước khi cutover prod nếu đường liên cloud đi Internet.
Mỗi lần nâng bậc chỉ sửa annotation và thêm Secret/Certificate, không đổi kiến trúc. Xem bảng "nâng từ bậc X" trong README của từng bậc.

Những file giống nhau ở mọi bậc: ConfigMap ingress-nginx của gc và sc.
Ở mỗi bậc chỉ có MỘT Ingress mẫu cho host `api.example.com`; mỗi host thêm thì nhân bản cặp Ingress (gc + sc) với host mới.
