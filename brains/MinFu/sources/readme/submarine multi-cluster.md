---
type: source
source_kind: own-note
status: processed
created: 2026-10-07
processed_at: 2026-10-07
wiki_links: ["[[wiki/devops/Kiến trúc Submariner đa VPC]]", "[[wiki/devops/CIDR và Globalnet cho Submariner]]", "[[wiki/devops/Triển khai và khám lỗi Submariner]]", "[[wiki/devops/Lighthouse và service discovery đa cluster]]", "[[wiki/devops/Đo latency và MTU của Submariner]]"]
url: null
original_path: "D:\\private01\\readme\\submarine multi-cluster.md"
original_sha256: add5535b6b60ce829c95db985ec96f033a1796e792a613a23252f87a1ff86e65

original_document_date: 2026-08-12
---

# Submariner Multi-Cluster Kubernetes trên FPT Cloud

## 1. Mục tiêu

Kết nối trực tiếp Service giữa hai Kubernetes cluster nằm trong hai VPC khác nhau trên FPT Cloud.

Mục tiêu:

```text
Cluster-A                                 Cluster-B

Pod A
  |
  | user-api.backend.svc.clusterset.local
  v
Lighthouse
  |
  v
Route Agent
  |
  v
Gateway-A  ============================>  Gateway-B
              Submariner VXLAN
              over private VPC path
                                              |
                                              v
                                         Service B
                                              |
                                              v
                                            Pod B
```

Yêu cầu chính:

- Hai cluster nằm ở hai VPC khác nhau.
- FPT cung cấp kết nối private giữa một subnet của VPC-A và một subnet của VPC-B.
- Submariner Gateway của mỗi cluster nằm trong subnet được FPT kết nối.
- Pod CIDR và Service CIDR giữa các cluster không overlap.
- Gateway private IP hai bên có L3 reachability.
- Firewall cho phép các port Submariner.
- Dùng Lighthouse để Service Discovery qua `*.svc.clusterset.local`.

---

## 2. Kết luận kiến trúc

Với topology hiện tại, mô hình khuyến nghị:

```text
                              CONTROL PLANE

                    +-------------------------+
                    |        Cluster-A        |
                    |                         |
                    | Submariner Broker       |
                    | submariner-k8s-broker   |
                    +------------+------------+
                                 ^
                                 |
                         Kubernetes API
                      metadata / ServiceExport
                                 |
                  +--------------+--------------+
                  |                             |
           Lighthouse A                  Lighthouse B


                               DATA PLANE

VPC-A                                              VPC-B
Cluster-A                                          Cluster-B

worker-a1                                          worker-b1
worker-a2                                          worker-b2
    |                                                  |
    | UDP/4800                                         | UDP/4800
    v                                                  v
gateway-a1                                        gateway-b1
gateway-a2                                        gateway-b2
    |                                                  ^
    |                                                  |
    +=============== UDP/4500 =========================+
                     Submariner VXLAN
                         over
             FPT private subnet connection

          NAT discovery / endpoint discovery:
                    UDP/4490
```

### Component nào cài ở cluster nào

| Component | Cluster-A | Cluster-B | Ghi chú |
|---|---:|---:|---|
| Submariner Broker | Yes | No | Chỉ cần một Broker |
| Submariner Operator | Yes | Yes | Được cài khi `join` |
| Gateway Engine | Yes | Yes | Chạy trên node có label gateway |
| Route Agent | Yes | Yes | DaemonSet trên các node |
| Lighthouse Agent | Yes | Yes | Đồng bộ Service metadata |
| Lighthouse DNS | Yes | Yes | Phục vụ `clusterset.local` |
| Globalnet | Optional | Optional | Chỉ cần khi CIDR overlap |

> Cluster-A chứa Broker vẫn phải `join` Broker như một participating cluster bình thường.

---

## 3. Các thành phần Submariner

### 3.1 Broker

Broker không phải một data-plane gateway.

Broker dùng để trao đổi metadata giữa các cluster:

- `Cluster`
- `Endpoint`
- `ServiceImport`
- `EndpointSlice`
- thông tin Gateway
- thông tin Service Discovery

Broker được deploy trên một cluster, ví dụ Cluster-A:

```bash
subctl deploy-broker --context cluster-a
```

Command tạo:

```text
submariner-k8s-broker
broker-info.subm
```

`broker-info.subm` chứa thông tin để cluster khác kết nối Broker.

---

### 3.2 Gateway Engine

Gateway Engine chịu trách nhiệm thiết lập inter-cluster tunnel.

Gateway pod chỉ chạy trên node có:

```text
submariner.io/gateway=true
```

Ví dụ:

```bash
kubectl --context cluster-a label node worker-a1 \
  submariner.io/gateway=true

kubectl --context cluster-b label node worker-b1 \
  submariner.io/gateway=true
```

Production nên có nhiều hơn một Gateway candidate.

Ví dụ:

```bash
kubectl --context cluster-a label node worker-a1 \
  submariner.io/gateway=true

kubectl --context cluster-a label node worker-a2 \
  submariner.io/gateway=true

kubectl --context cluster-b label node worker-b1 \
  submariner.io/gateway=true

kubectl --context cluster-b label node worker-b2 \
  submariner.io/gateway=true
```

Submariner dùng active/passive HA:

```text
Cluster-A                       Cluster-B

gateway-a1 ACTIVE              gateway-b1 ACTIVE
gateway-a2 STANDBY             gateway-b2 STANDBY
```

Tại mỗi cluster chỉ có một active Gateway tại một thời điểm.

---

### 3.3 Route Agent

Route Agent chạy trên các node.

Nhiệm vụ:

```text
Pod trên worker
      |
      | remote cluster traffic
      v
Route Agent
      |
      | internal VXLAN
      v
Active Gateway
```

Route Agent tự update route khi Gateway failover.

---

### 3.4 Lighthouse

Lighthouse cung cấp Multi-Cluster Service Discovery.

Flow:

```text
ServiceExport
     |
     v
Lighthouse Agent
     |
     v
Broker
     |
     v
Lighthouse Agent remote cluster
     |
     v
ServiceImport / EndpointSlice
     |
     v
Lighthouse DNS
```

Service được gọi bằng:

```text
<service>.<namespace>.svc.clusterset.local
```

Ví dụ:

```text
user-api.backend.svc.clusterset.local
```

Muốn ép gọi một cluster cụ thể:

```text
<cluster-id>.<service>.<namespace>.svc.clusterset.local
```

Ví dụ:

```text
cluster-b.user-api.backend.svc.clusterset.local
```

---

## 4. Kiểm tra requirement trước khi cài

### 4.1 Kiểm tra Kubernetes network

```bash
subctl show networks --context cluster-a
subctl show networks --context cluster-b
```

Kiểm tra trực tiếp:

```bash
kubectl --context cluster-a get nodes \
  -o custom-columns=NAME:.metadata.name,IP:.status.addresses[0].address,POD-CIDR:.spec.podCIDR

kubectl --context cluster-b get nodes \
  -o custom-columns=NAME:.metadata.name,IP:.status.addresses[0].address,POD-CIDR:.spec.podCIDR
```

---

### 4.2 Critical: kube-proxy mode

Theo Submariner Known Issues hiện tại:

```text
SUPPORTED:
kube-proxy iptables

NOT SUPPORTED:
kube-proxy IPVS
```

Phải check trước khi triển khai.

Ví dụ:

```bash
kubectl -n kube-system get cm kube-proxy -o yaml | grep -i mode
```

Hoặc:

```bash
kubectl -n kube-system get ds kube-proxy -o yaml | grep -i ipvs
```

Nếu FPT Managed Kubernetes đang chạy kube-proxy IPVS:

```text
STOP
```

Cần xác nhận lại compatibility với version Submariner/FPT trước khi production.

---

### 4.3 Kiểm tra CNI

```bash
subctl diagnose cni --context cluster-a
subctl diagnose cni --context cluster-b
```

Hoặc:

```bash
subctl diagnose all --context cluster-a
subctl diagnose all --context cluster-b
```

Không nên bỏ qua requirement check bằng:

```text
--ignore-requirements
```

trong production.

---

## 5. Thiết kế CIDR

FPT khuyến nghị address pool:

```text
Pod CIDR pool:
100.96.0.0/11

Service CIDR pool:
100.64.0.0/13
```

Không nên dùng nguyên block trên cho cả hai cluster.

Ví dụ sai:

```text
Cluster-A:
Pod:     100.96.0.0/11
Service: 100.64.0.0/13

Cluster-B:
Pod:     100.96.0.0/11
Service: 100.64.0.0/13
```

CIDR overlap nên Submariner non-Globalnet không dùng được.

### 5.1 Chia Pod CIDR

`100.96.0.0/11` có thể chia thành 8 block `/14`:

| Cluster | Pod CIDR |
|---|---|
| cluster-a | `100.96.0.0/14` |
| cluster-b | `100.100.0.0/14` |
| cluster-c | `100.104.0.0/14` |
| cluster-d | `100.108.0.0/14` |
| cluster-e | `100.112.0.0/14` |
| cluster-f | `100.116.0.0/14` |
| cluster-g | `100.120.0.0/14` |
| cluster-h | `100.124.0.0/14` |

Diagram:

```text
100.96.0.0/11
│
├── 100.96.0.0/14
├── 100.100.0.0/14
├── 100.104.0.0/14
├── 100.108.0.0/14
├── 100.112.0.0/14
├── 100.116.0.0/14
├── 100.120.0.0/14
└── 100.124.0.0/14
```

---

### 5.2 Chia Service CIDR

`100.64.0.0/13` có thể chia thành 8 block `/16`:

| Cluster | Service CIDR |
|---|---|
| cluster-a | `100.64.0.0/16` |
| cluster-b | `100.65.0.0/16` |
| cluster-c | `100.66.0.0/16` |
| cluster-d | `100.67.0.0/16` |
| cluster-e | `100.68.0.0/16` |
| cluster-f | `100.69.0.0/16` |
| cluster-g | `100.70.0.0/16` |
| cluster-h | `100.71.0.0/16` |

Diagram:

```text
100.64.0.0/13
│
├── 100.64.0.0/16
├── 100.65.0.0/16
├── 100.66.0.0/16
├── 100.67.0.0/16
├── 100.68.0.0/16
├── 100.69.0.0/16
├── 100.70.0.0/16
└── 100.71.0.0/16
```

---

### 5.3 CIDR đề xuất cho hai cluster

```text
CLUSTER-A

VPC / Node subnet:     ví dụ 10.10.0.0/16
Gateway subnet:        ví dụ 10.10.10.0/24
Pod CIDR:              100.96.0.0/14
Service CIDR:          100.64.0.0/16


CLUSTER-B

VPC / Node subnet:     ví dụ 10.20.0.0/16
Gateway subnet:        ví dụ 10.20.10.0/24
Pod CIDR:              100.100.0.0/14
Service CIDR:          100.65.0.0/16
```

Không overlap:

```text
100.96.0.0/14  != 100.100.0.0/14
100.64.0.0/16  != 100.65.0.0/16
```

Ngoài ra nên đảm bảo:

```text
VPC CIDR
Node subnet
Pod CIDR
Service CIDR
```

không conflict với nhau trong routing domain.

> Lưu ý: việc FPT Managed Kubernetes có chấp nhận chính xác prefix `/14` và `/16` hay không cần validate trên Portal/API của FPT trước khi tạo cluster. Đây là cách chia CIDR hợp lệ về mặt IP planning, không phải tuyên bố constraint của MFKE.

---

## 6. Khi nào cần Globalnet

Nếu hai cluster bắt buộc dùng cùng CIDR:

```text
Cluster-A:
Pod:     100.96.0.0/11
Service: 100.64.0.0/13

Cluster-B:
Pod:     100.96.0.0/11
Service: 100.64.0.0/13
```

thì phải bật Globalnet:

```bash
subctl deploy-broker \
  --context cluster-a \
  --globalnet
```

Sau đó join các cluster.

Nếu thiết kế được CIDR không overlap từ đầu:

```text
PREFERRED:
không dùng Globalnet
```

Topology đơn giản hơn và troubleshoot dễ hơn.

---

## 7. FPT chỉ kết nối hai subnet giữa hai VPC có dùng được không?

Có.

Submariner không yêu cầu:

```text
worker-a1 -> worker-b1
worker-a2 -> worker-b2
worker-a3 -> worker-b3
```

phải direct route qua FPT VPC Peering.

Điều quan trọng là:

```text
Gateway-A private IP
        ↕
Gateway-B private IP
```

có reachability.

### Topology phù hợp với constraint FPT

```text
VPC-A                                          VPC-B

Cluster-A                                      Cluster-B

worker-a1                                      worker-b1
worker-a2                                      worker-b2
    |                                              |
    | UDP/4800                                     | UDP/4800
    v                                              v

Subnet-A được FPT kết nối                  Subnet-B được FPT kết nối
10.10.10.0/24                             10.20.10.0/24

gateway-a1                                 gateway-b1
10.10.10.11                               10.20.10.11

gateway-a2                                 gateway-b2
10.10.10.12                               10.20.10.12

       <======= FPT private connection =======>
```

Data path:

```text
Pod A
 |
 v
Route Agent
 |
 | UDP/4800
 v
Gateway A
 |
 | UDP/4500
 | VXLAN dataplane
 v
FPT private subnet path
 |
 v
Gateway B
 |
 v
Remote Pod / Service
```

FPT không cần route trực tiếp:

```text
100.96.0.0/14
        ↕
100.100.0.0/14
```

qua VPC peering.

Submariner Gateway xử lý tunnel cho phần cross-cluster Pod/Service traffic.

---

## 8. Điều cần xác nhận với FPT

Câu trả lời hiện tại từ FPT:

```text
"Hiện bên em chỉ hỗ trợ kết nối 2 subnet giữa 2 VPC"
```

là đủ để thiết kế theo hướng Gateway subnet, nhưng trước khi triển khai cần xác nhận:

```text
1. Hai subnet sau khi kết nối có route Layer-3 hai chiều bằng private IP không?

2. VM/node trong subnet-A có thể gửi UDP trực tiếp tới VM/node trong subnet-B không?

3. Có cho phép UDP/4490 và UDP/4500 hai chiều không?

4. Có NAT/SNAT giữa hai subnet không?

5. IP nguồn có được giữ nguyên không?

6. Traffic VPC Peering/subnet connection có được mã hóa không?

7. Security Group / Firewall nào kiểm soát traffic giữa hai subnet?
```

Nếu:

```text
Gateway-A private IP -> Gateway-B private IP
```

route được và UDP dataplane được phép thì Submariner có nền tảng network cần thiết để hoạt động.

---

## 9. Chọn cable driver

Submariner hiện hỗ trợ:

```text
libreswan
wireguard
vxlan
```

### 9.1 Case hiện tại: VXLAN

Khuyến nghị:

```bash
--cable-driver vxlan
```

khi:

- Gateway A và B direct reachability bằng private IP.
- Không có NAT giữa Gateway.
- Underlay là private VPC/VPC peering.
- Underlay đã được bảo vệ hoặc chấp nhận không encrypt ở layer Submariner.

VXLAN của Submariner:

```text
UNENCRYPTED
```

Do đó cần xác định security requirement.

### 9.2 Nếu FPT underlay đã được mã hóa

```text
Submariner VXLAN
       over
FPT encrypted/private underlay
```

tránh double encryption.

### 9.3 Nếu FPT private path không encrypt và yêu cầu confidentiality

Cân nhắc:

```text
libreswan
```

hoặc:

```text
wireguard
```

thay cho VXLAN.

---

## 10. Firewall / Security Group

### 10.1 Inter-cluster ports

Gateway A ↔ Gateway B:

```text
UDP/4490
NAT-T / endpoint reachability discovery

UDP/4500
Submariner dataplane tunnel
IPsec / WireGuard / VXLAN
```

Ví dụ:

```text
Subnet-A:
10.10.10.0/24

Subnet-B:
10.20.10.0/24
```

Cluster-A / Gateway Security Group:

```text
INBOUND

Source:      10.20.10.0/24
Protocol:    UDP
Ports:       4490,4500
```

Nếu outbound bị restrict:

```text
OUTBOUND

Destination: 10.20.10.0/24
Protocol:    UDP
Ports:       4490,4500
```

Cluster-B:

```text
INBOUND

Source:      10.10.10.0/24
Protocol:    UDP
Ports:       4490,4500
```

Outbound tương ứng nếu policy outbound không allow-all.

FPT VPC Peering cần route table và Security Group/Firewall cho phép traffic thích hợp giữa VPC/subnet.

---

### 10.2 Intra-cluster port

Trong mỗi cluster:

```text
UDP/4800
```

là internal VXLAN dùng để đưa cross-cluster traffic từ worker/master node về Gateway node.

Cluster-A:

```text
worker-a1 ----\
worker-a2 -----+--- UDP/4800 ---> active Gateway-A
worker-a3 ----/
```

Cluster-B:

```text
worker-b1 ----\
worker-b2 -----+--- UDP/4800 ---> active Gateway-B
worker-b3 ----/
```

Rule điển hình:

```text
Cluster-A node CIDR -> Cluster-A node CIDR
UDP/4800

Cluster-B node CIDR -> Cluster-B node CIDR
UDP/4800
```

---

### 10.3 Port matrix

| Scope | Port | Protocol | Purpose |
|---|---:|---|---|
| Gateway A ↔ Gateway B | 4490 | UDP | NAT/endpoint discovery |
| Gateway A ↔ Gateway B | 4500 | UDP | Inter-cluster dataplane |
| Node ↔ Gateway cùng cluster | 4800 | UDP | Internal VXLAN |
| Monitoring nếu sử dụng | 8080 | TCP | Gateway metrics |

---

## 11. Kiểm tra route giữa Gateway

Giả sử:

```text
Gateway-A: 10.10.10.11
Gateway-B: 10.20.10.11
```

Trên Gateway-A:

```bash
ip route get 10.20.10.11
```

Trên Gateway-B:

```bash
ip route get 10.10.10.11
```

Nếu ICMP được phép:

```bash
ping 10.20.10.11
```

và:

```bash
ping 10.10.10.11
```

Có thể dùng netcat kiểm tra UDP, nhưng nên dùng chính diagnostic của Submariner sau khi cài:

```bash
subctl diagnose firewall inter-cluster \
  --context cluster-a \
  --remotecontext cluster-b \
  --verbose
```

Và:

```bash
subctl diagnose firewall intra-cluster \
  --context cluster-a \
  --verbose

subctl diagnose firewall intra-cluster \
  --context cluster-b \
  --verbose
```

---

## 12. Cài subctl

Trên máy admin/DevOps:

```bash
curl -Ls https://get.submariner.io | bash

export PATH="$PATH:$HOME/.local/bin"

subctl version
```

Nên pin version trong production thay vì luôn dùng latest.

Ví dụ pattern:

```bash
export VERSION=<approved-version>
curl -Ls https://get.submariner.io | bash
```

Version `subctl` và Submariner component nên đồng bộ.

---

## 13. Deploy Broker

Chọn Cluster-A làm Broker:

```bash
subctl deploy-broker \
  --context cluster-a
```

Kiểm tra:

```bash
kubectl --context cluster-a get ns | grep submariner
```

```bash
kubectl --context cluster-a get crd | grep -E 'submariner|multicluster'
```

Output mong đợi có các CRD như:

```text
clusters.submariner.io
endpoints.submariner.io
gateways.submariner.io

serviceexports.multicluster.x-k8s.io
serviceimports.multicluster.x-k8s.io
```

Broker tạo:

```text
broker-info.subm
```

---

## 14. Join Cluster-A

Cluster chứa Broker vẫn phải join.

```bash
subctl join broker-info.subm \
  --context cluster-a \
  --clusterid cluster-a \
  --clustercidr 100.96.0.0/14 \
  --servicecidr 100.64.0.0/16 \
  --cable-driver vxlan
```

---

## 15. Join Cluster-B

```bash
subctl join broker-info.subm \
  --context cluster-b \
  --clusterid cluster-b \
  --clustercidr 100.100.0.0/14 \
  --servicecidr 100.65.0.0/16 \
  --cable-driver vxlan
```

Cluster ID phải unique.

---

## 16. Kiểm tra component sau khi join

Cluster-A:

```bash
kubectl --context cluster-a \
  -n submariner-operator get pods -o wide
```

Cluster-B:

```bash
kubectl --context cluster-b \
  -n submariner-operator get pods -o wide
```

Thông thường sẽ có:

```text
submariner-operator
submariner-gateway
submariner-routeagent
submariner-lighthouse-agent
submariner-lighthouse-coredns
```

Check DaemonSet:

```bash
kubectl --context cluster-a \
  -n submariner-operator get ds

kubectl --context cluster-b \
  -n submariner-operator get ds
```

---

## 17. Kiểm tra Gateway

```bash
subctl show gateways --context cluster-a
subctl show gateways --context cluster-b
```

```bash
subctl show endpoints --context cluster-a
subctl show endpoints --context cluster-b
```

```bash
subctl show connections --context cluster-a
subctl show connections --context cluster-b
```

Mục tiêu:

```text
STATUS: connected
```

---

## 18. Verify toàn bộ deployment

```bash
subctl verify \
  --context cluster-a \
  --tocontext cluster-b \
  --only connectivity,service-discovery \
  --verbose
```

Connectivity suite kiểm tra các flow như:

```text
Gateway Pod     -> remote Service
Non-Gateway Pod -> remote Service
Gateway Pod     -> remote Pod
Non-Gateway Pod -> remote Pod
```

Service Discovery suite kiểm tra:

```text
<service>.<namespace>.svc.clusterset.local
```

---

## 19. Benchmark latency và throughput

Submariner có benchmark built-in.

Latency:

```bash
subctl benchmark latency \
  --context cluster-a \
  --tocontext cluster-b \
  --verbose
```

Throughput:

```bash
subctl benchmark throughput \
  --context cluster-a \
  --tocontext cluster-b \
  --verbose
```

Nên chạy baseline ngay sau khi cài để có số liệu so sánh về sau.

---

## 20. Export Service

Giả sử Cluster-B có:

```text
namespace: backend
service:   user-api
port:      8080
```

### 20.1 Dùng subctl

```bash
subctl export service user-api \
  --namespace backend \
  --context cluster-b
```

---

### 20.2 Dùng manifest

Khuyến nghị nếu quản lý bằng GitOps/ArgoCD:

```yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: user-api
  namespace: backend
```

Apply:

```bash
kubectl --context cluster-b apply -f service-export.yaml
```

`ServiceExport` phải:

```text
same name
same namespace
```

với Service gốc.

Ví dụ:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: user-api
  namespace: backend
spec:
  selector:
    app: user-api
  ports:
    - name: http
      port: 8080
      targetPort: 8080
---
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: user-api
  namespace: backend
```

ArgoCD có thể quản lý cả hai manifest này.

---

## 21. Check ServiceExport / ServiceImport

Cluster-B:

```bash
kubectl --context cluster-b \
  -n backend get serviceexport user-api
```

Cluster-A:

```bash
kubectl --context cluster-a \
  -n backend get serviceimport user-api
```

Check EndpointSlice:

```bash
kubectl --context cluster-a \
  get endpointslices \
  -A \
  -l multicluster.kubernetes.io/service-name=user-api
```

---

## 22. Gọi Service từ Cluster-A

Tạo test Pod:

```bash
kubectl --context cluster-a run curl-test \
  --rm -it \
  --image=curlimages/curl \
  -- sh
```

DNS:

```bash
nslookup user-api.backend.svc.clusterset.local
```

Call:

```bash
curl http://user-api.backend.svc.clusterset.local:8080
```

Ép gọi riêng Cluster-B:

```bash
curl http://cluster-b.user-api.backend.svc.clusterset.local:8080
```

---

## 23. Nếu cùng Service được deploy ở hai cluster

Ví dụ cả hai cluster đều có:

```text
backend/user-api
```

và cả hai đều `ServiceExport`.

Khi Pod gọi:

```text
user-api.backend.svc.clusterset.local
```

Lighthouse ưu tiên local cluster nếu Service tồn tại local.

Nếu client nằm ở một cluster thứ ba, hoặc local Service không tồn tại, Lighthouse có thể trả remote cluster còn healthy.

Muốn chỉ định chính xác:

```text
cluster-b.user-api.backend.svc.clusterset.local
```

---

## 24. Broker connectivity

Không được nhầm Broker path với dataplane.

```text
CONTROL PLANE

Lighthouse B
    |
    | Kubernetes API
    v
Broker trên Cluster-A


DATA PLANE

Gateway A
    |
    | UDP/4500
    v
Gateway B
```

Cluster-B phải truy cập được Kubernetes API endpoint của Broker cluster.

Nếu Kubernetes API Cluster-A là public:

```text
Cluster-B -> public Kubernetes API
```

Nếu private:

```text
Cluster-B -> private Kubernetes API
```

phải có route/firewall phù hợp.

---

## 25. Production topology

Không nên production với chỉ một Gateway candidate mỗi cluster.

Recommended:

```text
                    FPT CLOUD

VPC-A                                         VPC-B

Gateway subnet-A                             Gateway subnet-B
10.10.10.0/24                               10.20.10.0/24

gateway-a1                                  gateway-b1
10.10.10.11                                 10.20.10.11
ACTIVE                                      ACTIVE

gateway-a2                                  gateway-b2
10.10.10.12                                 10.20.10.12
STANDBY                                     STANDBY

      <====== FPT subnet connectivity ======>
                  UDP 4490/4500


Cluster-A                                   Cluster-B

Pod:     100.96.0.0/14                     Pod:     100.100.0.0/14
Service: 100.64.0.0/16                     Service: 100.65.0.0/16
```

Tất cả Gateway candidate phải nằm trong subnet mà FPT route sang VPC còn lại, hoặc FPT phải hỗ trợ route tới subnet chứa chúng.

---

## 26. Mức độ phù hợp production

Submariner là kiến trúc multi-cluster networking hợp lệ cho production.

Nó phù hợp khi cần:

```text
multi-cluster
multi-VPC
hybrid cloud
multi-cloud
direct Pod/Service connectivity
Kubernetes-native ServiceExport/ServiceImport
```

Không nên coi cross-cluster call là default cho mọi microservice.

Pattern tốt hơn:

```text
Cluster-A                  Cluster-B

local service              local service
     |                          |
     +------ Submariner --------+
         cross-cluster khi cần
```

thay vì:

```text
mọi request của Service-A
        |
        v
remote Service-B
```

Cross-cluster dependency làm tăng:

- failure domain coupling
- network dependency
- latency sensitivity
- complexity khi troubleshoot
- blast radius khi remote cluster/network lỗi

---

## 27. Submariner có gây latency không?

Có thể.

Submariner nằm trong dataplane nên không phải zero-cost bridge.

Latency path:

```text
Total latency
 =
Pod/CNI local
+ Route Agent
+ worker -> Gateway
+ VXLAN encapsulation
+ inter-VPC RTT
+ VXLAN decapsulation
+ remote CNI
+ application
+ DB/cache/external dependency
```

Tuy nhiên trong topology tốt:

```text
Gateway CPU       OK
Gateway NIC       OK
MTU               OK
packet loss       ~0
private network   stable
```

thì Submariner VXLAN thường không phải nơi cần nghi đầu tiên khi API có application latency lớn.

---

## 28. Cách isolate latency

### Test 1 — Underlay

Gateway-A:

```bash
ping 10.20.10.11
```

Đo:

```text
FPT subnet-A <-> subnet-B RTT
```

---

### Test 2 — Pod-to-Pod qua Submariner

```bash
ping <remote-pod-ip>
```

Đo:

```text
Pod
-> CNI
-> Route Agent
-> Gateway
-> Submariner
-> Gateway
-> CNI
-> Pod
```

---

### Test 3 — Built-in benchmark

```bash
subctl benchmark latency \
  --context cluster-a \
  --tocontext cluster-b \
  --verbose
```

---

### Test 4 — HTTP Service

```bash
curl -o /dev/null \
  -s \
  -w '
dns=%{time_namelookup}
connect=%{time_connect}
ttfb=%{time_starttransfer}
total=%{time_total}
\n' \
  http://user-api.backend.svc.clusterset.local:8080/health
```

Ví dụ:

```text
dns=0.002
connect=0.004
ttfb=0.087
total=0.088
```

Nếu:

```text
connect = 4 ms
TTFB    = 87 ms
```

thì phần lớn delay nhiều khả năng nằm sau TCP connect:

```text
application
DB
Redis
Kafka
external API
```

không phải tunnel establishment/network connect.

---

## 29. Test bằng service đơn giản

Để isolate Submariner khỏi application:

```text
Cluster-A Pod
     |
     v
simple nginx/echo Service
Cluster-B
```

Service test không nên có:

```text
DB
Redis
Kafka
external dependency
business logic
```

So sánh:

```text
#1 Gateway -> Gateway
#2 Pod -> Pod
#3 Pod -> simple HTTP Service
#4 Pod -> real application
```

Ví dụ:

```text
Gateway -> Gateway       1.0 ms
Pod -> Pod               1.6 ms
simple HTTP              2.3 ms
real API                90.0 ms
```

Root cause chính khi đó không nằm ở Submariner.

---

## 30. MTU / MSS

VXLAN thêm encapsulation overhead.

Nếu MTU không đủ:

```text
packet fragmentation
packet drop
TCP retransmission
latency spike
throughput giảm
```

Test:

```bash
ping -M do -s 1400 <remote-pod-ip>
ping -M do -s 1420 <remote-pod-ip>
ping -M do -s 1440 <remote-pod-ip>
ping -M do -s 1460 <remote-pod-ip>
ping -M do -s 1472 <remote-pod-ip>
```

Nếu packet nhỏ OK nhưng packet lớn fail:

```text
SUSPECT:
MTU / MSS
```

Submariner hỗ trợ TCP MSS clamping trên Gateway node.

Ví dụ:

```bash
kubectl annotate node <gateway-node> \
  submariner.io/tcp-clamp-mss=<value>

kubectl delete pod \
  -n submariner-operator \
  -l app=submariner-routeagent
```

Không set MSS tùy ý nếu chưa đo MTU path.

---

## 31. Gateway bottleneck

Active Gateway là điểm cross-cluster traffic tập trung.

Check:

```bash
kubectl -n submariner-operator top pod
```

```bash
kubectl top node
```

Check Gateway pod:

```bash
kubectl -n submariner-operator \
  get pods \
  -l app=submariner-gateway \
  -o wide
```

Nếu:

```text
Gateway CPU high
NIC saturated
packet loss
```

thì Submariner path có thể trở thành bottleneck.

HA active/passive tăng availability nhưng không biến hai Gateway thành active-active load sharing.

---

## 32. Gateway health

Submariner Gateway health check theo dõi connected cluster và RTT.

```bash
subctl show connections --context cluster-a
```

```bash
kubectl --context cluster-a \
  get gateways.submariner.io -A -o yaml
```

Nên theo dõi:

```text
connection status
RTT
average latency
gateway failover
packet loss
```

---

## 33. External Load Balancer có nằm trong path không?

Nếu Pod gọi:

```text
user-api.backend.svc.clusterset.local
```

thì external FPT Load Balancer/Ingress thường không nằm trong path.

Flow:

```text
Pod
 -> Kubernetes networking
 -> Submariner
 -> Kubernetes networking
 -> remote Service/Pod
```

khác với:

```text
User
 -> FPT Load Balancer
 -> Ingress
 -> Service
 -> Pod
```

Do đó cross-cluster Service latency không nên mặc định đổ lỗi cho external LB.

---

## 34. North-south và east-west

Submariner giải quyết:

```text
Cluster-A <------ east-west ------> Cluster-B
```

Không trực tiếp giải quyết:

```text
User -> nearest cluster
```

Nếu mục tiêu là active-active multi-region:

```text
                   GSLB / GeoDNS
                        |
             +----------+----------+
             |                     |
             v                     v
         Cluster-A             Cluster-B
             |                     |
             +---- Submariner -----+
                  khi cần east-west
```

North-south failover vẫn cần:

- GeoDNS/GSLB
- health check
- DNS/LB failover
- database/state strategy

---

## 35. Troubleshooting

### Problem: Gateway không connected

#### Check

```bash
subctl show connections --context cluster-a
```

```bash
subctl show endpoints --context cluster-a
```

```bash
subctl diagnose connections --context cluster-a
```

```bash
subctl diagnose firewall inter-cluster \
  --context cluster-a \
  --remotecontext cluster-b \
  --verbose
```

#### Suspect

```text
FPT route
Security Group
UDP/4490
UDP/4500
Gateway subnet
NAT
wrong endpoint IP
```

---

### Problem: Pod worker không gọi được remote, Gateway gọi được

#### Check

```bash
subctl diagnose firewall intra-cluster \
  --context cluster-a \
  --verbose
```

#### Suspect

```text
UDP/4800
Route Agent
CNI
node routing
rp_filter
```

---

### Problem: DNS `clusterset.local` không resolve

#### Check

```bash
kubectl -n kube-system describe configmap coredns
```

Tìm:

```text
clusterset.local:53
```

Check Lighthouse:

```bash
kubectl -n submariner-operator \
  get pods \
  -l app=submariner-lighthouse-agent
```

Check ServiceImport:

```bash
kubectl get serviceimports -A
```

Check EndpointSlice:

```bash
kubectl get endpointslices -A \
  -l multicluster.kubernetes.io/service-name=<service>
```

---

### Problem: ServiceImport không xuất hiện

#### Check source cluster

```bash
kubectl --context cluster-b \
  -n backend get serviceexport user-api
```

#### Check Broker

```bash
kubectl --context cluster-a \
  get serviceimports -A
```

#### Check Lighthouse logs

```bash
kubectl --context cluster-b \
  -n submariner-operator logs \
  deployment/submariner-lighthouse-agent
```

---

### Problem: Latency spike

#### Commands trước

```bash
ping <remote-gateway-ip>
```

```bash
subctl benchmark latency \
  --context cluster-a \
  --tocontext cluster-b \
  --verbose
```

```bash
kubectl top node
```

```bash
kubectl -n submariner-operator top pod
```

```bash
ping -M do -s 1400 <remote-pod-ip>
```

#### Suspect order

```text
1. FPT underlay RTT / packet loss
2. Gateway CPU / NIC
3. MTU / retransmission
4. CNI / routing
5. Submariner tunnel
6. application
7. DB/cache/external dependencies
```

Thứ tự thực tế cần điều chỉnh theo metric `connect`, `TTFB`, RTT và application trace.

---

## 36. Production checklist

### Network

- [ ] VPC CIDR không conflict.
- [ ] Pod CIDR giữa clusters không overlap.
- [ ] Service CIDR giữa clusters không overlap.
- [ ] Gateway node nằm trong subnet được FPT kết nối.
- [ ] Gateway-A private IP route được Gateway-B private IP.
- [ ] UDP/4490 allowed hai chiều.
- [ ] UDP/4500 allowed hai chiều.
- [ ] UDP/4800 allowed trong từng cluster.
- [ ] Broker Kubernetes API reachable.
- [ ] MTU path đã benchmark.
- [ ] Packet loss baseline đã có.

### Kubernetes

- [ ] `kube-proxy` đang ở `iptables`.
- [ ] CNI pass `subctl diagnose cni`.
- [ ] CoreDNS hoạt động.
- [ ] `subctl diagnose deployment` pass.
- [ ] Gateway candidate tối thiểu 2 node/cluster nếu yêu cầu HA.
- [ ] Gateway candidate đều nằm trong subnet routable.
- [ ] Resource Gateway node đủ CPU/NIC.

### Submariner

- [ ] Broker deploy thành công.
- [ ] Cluster-A join Broker.
- [ ] Cluster-B join Broker.
- [ ] Cable driver = `vxlan` nếu underlay security phù hợp.
- [ ] `subctl show connections` = connected.
- [ ] `subctl verify` pass.
- [ ] `subctl benchmark latency` đã lưu baseline.
- [ ] `subctl benchmark throughput` đã lưu baseline.
- [ ] Gateway failover đã test.

### Service Discovery

- [ ] `ServiceExport` tồn tại.
- [ ] `ServiceImport` được tạo ở remote cluster.
- [ ] `EndpointSlice` đúng.
- [ ] `*.svc.clusterset.local` resolve.
- [ ] Cluster-specific DNS resolve.

---

## 37. Command flow ngắn gọn

### Cluster network

```bash
subctl show networks --context cluster-a
subctl show networks --context cluster-b
```

### Label Gateway

```bash
kubectl --context cluster-a label node worker-a1 submariner.io/gateway=true
kubectl --context cluster-a label node worker-a2 submariner.io/gateway=true

kubectl --context cluster-b label node worker-b1 submariner.io/gateway=true
kubectl --context cluster-b label node worker-b2 submariner.io/gateway=true
```

### Deploy Broker

```bash
subctl deploy-broker --context cluster-a
```

### Join Cluster-A

```bash
subctl join broker-info.subm \
  --context cluster-a \
  --clusterid cluster-a \
  --clustercidr 100.96.0.0/14 \
  --servicecidr 100.64.0.0/16 \
  --cable-driver vxlan
```

### Join Cluster-B

```bash
subctl join broker-info.subm \
  --context cluster-b \
  --clusterid cluster-b \
  --clustercidr 100.100.0.0/14 \
  --servicecidr 100.65.0.0/16 \
  --cable-driver vxlan
```

### Check

```bash
subctl show all --context cluster-a
subctl show all --context cluster-b
```

### Diagnose firewall

```bash
subctl diagnose firewall intra-cluster \
  --context cluster-a \
  --verbose

subctl diagnose firewall intra-cluster \
  --context cluster-b \
  --verbose

subctl diagnose firewall inter-cluster \
  --context cluster-a \
  --remotecontext cluster-b \
  --verbose
```

### Verify

```bash
subctl verify \
  --context cluster-a \
  --tocontext cluster-b \
  --only connectivity,service-discovery \
  --verbose
```

### Export Service

```yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: user-api
  namespace: backend
```

### Test

```bash
curl http://user-api.backend.svc.clusterset.local:8080
```

Hoặc:

```bash
curl http://cluster-b.user-api.backend.svc.clusterset.local:8080
```

### Benchmark

```bash
subctl benchmark latency \
  --context cluster-a \
  --tocontext cluster-b \
  --verbose

subctl benchmark throughput \
  --context cluster-a \
  --tocontext cluster-b \
  --verbose
```

---

## 38. Architecture cuối cùng

```text
                                  FPT CLOUD

                    CONTROL PLANE / METADATA

                   +-------------------------+
                   |        Cluster-A        |
                   |                         |
                   | Submariner Broker       |
                   +------------+------------+
                                ^
                                |
                     Kubernetes API / metadata
                                |
               +----------------+----------------+
               |                                 |
       Lighthouse Agent A                Lighthouse Agent B


                         DATA PLANE

 VPC-A                                                 VPC-B
 Cluster-A                                             Cluster-B

 Pod A                                                 Pod B
   |                                                     ^
   |                                                     |
 Route Agent A                                      Route Agent B
   |                                                     ^
   | UDP/4800                                            | UDP/4800
   v                                                     |
 Gateway-A ACTIVE                                  Gateway-B ACTIVE
 Gateway-A STANDBY                                Gateway-B STANDBY
   |                                                     ^
   |                                                     |
   +-------------------- UDP/4500 -----------------------+
                 Submariner VXLAN dataplane
                            |
              FPT subnet-to-subnet private path
                            |
                    UDP/4490 discovery


 Pod CIDR:                                           Pod CIDR:
 100.96.0.0/14                                      100.100.0.0/14

 Service CIDR:                                       Service CIDR:
 100.64.0.0/16                                      100.65.0.0/16
```

---

## 39. Kết luận

Với constraint FPT:

```text
VPC-A chỉ kết nối được một subnet
            ↕
VPC-B chỉ kết nối được một subnet
```

Submariner vẫn phù hợp nếu:

```text
Gateway nodes của Cluster-A
nằm trong subnet-A

Gateway nodes của Cluster-B
nằm trong subnet-B

subnet-A <-> subnet-B
có L3 private connectivity

UDP/4490 + UDP/4500 thông

các node trong cluster
UDP/4800 thông

Pod/Service CIDR không overlap

kube-proxy = iptables
```

Cable driver khuyến nghị cho topology private peering:

```text
vxlan
```

nếu security của underlay đáp ứng yêu cầu.

Submariner là thành phần dataplane nên có overhead, nhưng có thể đo và isolate bằng:

```text
Gateway RTT
Pod-to-Pod RTT
subctl benchmark latency
subctl benchmark throughput
HTTP connect / TTFB
Gateway CPU/NIC
MTU/MSS
```

Không nên mặc định kết luận Submariner là root cause khi application chậm.

---

## 40. References

Nguồn chính dùng để xây dựng tài liệu:

1. Submariner — Architecture
   - https://submariner.io/getting-started/architecture/

2. Submariner — Gateway Engine
   - https://submariner.io/getting-started/architecture/gateway-engine/

3. Submariner — Service Discovery / Lighthouse
   - https://submariner.io/getting-started/architecture/service-discovery/

4. Submariner — Globalnet Controller
   - https://submariner.io/getting-started/architecture/globalnet/

5. Submariner — subctl
   - https://submariner.io/operations/deployment/subctl/

6. Submariner — NAT Traversal
   - https://submariner.io/operations/nat-traversal/

7. Submariner — User Guide
   - https://submariner.io/operations/usage/

8. Submariner — Troubleshooting
   - https://submariner.io/operations/troubleshooting/

9. Submariner — Known Issues
   - https://submariner.io/operations/known-issues/

10. FPT Cloud — VPC Peering
    - https://docs.fptcloud.com/vi/docs/category/vpc-peering/

> Tài liệu được tổng hợp ngày 2026-08-12. Trước khi production nên pin một version Submariner cụ thể và đối chiếu Known Issues/compatibility của version đó với Kubernetes, CNI và kube-proxy trên FPT Managed Kubernetes.
