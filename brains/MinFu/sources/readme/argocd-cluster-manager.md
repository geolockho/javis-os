---
type: source
source_kind: own-note
status: processed
created: 2026-10-07
processed_at: 2026-10-07
wiki_links: ["[[wiki/devops/Argo CD đa cluster]]", "[[wiki/devops/Quản lý kubeconfig nhiều cluster]]", "[[wiki/devops/Phân quyền và credential Argo CD]]", "[[wiki/devops/ApplicationSet và GitOps đa cluster]]", "[[wiki/devops/Lighthouse và service discovery đa cluster]]"]
url: null
original_path: "D:\\private01\\readme\\argocd-cluster-manager.md"
original_sha256: f142b229c84be41877fc516caced3490d71ec92fc948a5f1e7c91648f9e77da0
---

# Argo CD Multi-Cluster Setup

## 1. Mục tiêu

Thiết lập một Argo CD trung tâm để quản lý và triển khai ứng dụng tới nhiều Kubernetes cluster.

```text
                         GitLab / GitHub
                                |
                                v
                    +----------------------+
                    | Argo CD              |
                    | Management Cluster   |
                    +----------+-----------+
                               |
             Kubernetes API HTTPS/6443 hoặc 443
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
    fsel-prod            fsel-premium          guruit
```

Argo CD kết nối trực tiếp tới Kubernetes API Server của từng target cluster.

Target cluster không cần cài thêm Argo CD Agent.

Khi chạy `argocd cluster add`, Argo CD sẽ:

* Sử dụng context trong kubeconfig.
* Tạo ServiceAccount và RBAC trên target cluster.
* Lấy credential của ServiceAccount.
* Lưu thông tin kết nối dưới dạng Secret trong namespace `argocd`.
* Sử dụng credential đó để theo dõi và triển khai resource.

---

# 2. Điều kiện cần

Máy thực hiện cấu hình cần có:

```bash
kubectl version --client
argocd version --client
```

Cần có quyền:

* Truy cập Kubernetes API của tất cả target cluster.
* Tạo ServiceAccount, ClusterRole và ClusterRoleBinding trên target cluster.
* Đăng nhập được vào Argo CD.
* Truy cập được Git repository chứa manifest.

Kiểm tra network:

```bash
nc -vz api.djtaj383.prd.m.fke.fptcloud.com 443
nc -vz api.idf94uj8.prd.m.fke.fptcloud.com 443
nc -vz kube.guruit.vn 443
```

Hoặc:

```bash
curl -vk https://api.djtaj383.prd.m.fke.fptcloud.com/version
curl -vk https://api.idf94uj8.prd.m.fke.fptcloud.com/version
curl -vk https://kube.guruit.vn/version
```

HTTP `401 Unauthorized` là kết quả chấp nhận được trong bước kiểm tra network.

Điều quan trọng là:

* DNS resolve được.
* TCP connection thành công.
* TLS handshake thành công.
* Không timeout.
* Không bị certificate mismatch.

---

# 3. Cấu trúc thư mục đề xuất

```text
argocd-multi-cluster/
├── README.md
├── kubeconfig/
│   └── all-clusters.yaml
├── projects/
│   ├── platform.yaml
│   └── applications.yaml
├── applicationsets/
│   ├── platform-applicationset.yaml
│   └── services-applicationset.yaml
├── bootstrap/
│   └── root-application.yaml
└── services/
    ├── tracking-api/
    │   ├── values-unstable.yaml
    │   ├── values-staging.yaml
    │   └── values-prod.yaml
    └── auth/
        ├── values-unstable.yaml
        ├── values-staging.yaml
        └── values-prod.yaml
```

Không commit file kubeconfig thật vào Git repository.

Thêm vào `.gitignore`:

```gitignore
kubeconfig/*.yaml
*.kubeconfig
```

---

# 4. Tạo kubeconfig tổng

## 4.1. Mục đích

Kubeconfig tổng chứa context của toàn bộ Kubernetes cluster mà Argo CD cần quản lý.

Ví dụ:

```text
fsel-prod
fsel-premium
guruit
```

Argo CD CLI sẽ sử dụng các context này khi chạy:

```bash
argocd cluster add <context-name>
```

---

## 4.2. Kiểm tra kubeconfig từng cluster

Ví dụ có các file:

```text
/root/.kube/fsel-prod.yaml
/root/.kube/fsel-premium.yaml
/root/.kube/guruit.yaml
```

Kiểm tra từng file:

```bash
KUBECONFIG=/root/.kube/fsel-prod.yaml \
kubectl config get-contexts
```

```bash
KUBECONFIG=/root/.kube/fsel-premium.yaml \
kubectl config get-contexts
```

```bash
KUBECONFIG=/root/.kube/guruit.yaml \
kubectl config get-contexts
```

Test kết nối:

```bash
KUBECONFIG=/root/.kube/fsel-prod.yaml \
kubectl get nodes
```

```bash
KUBECONFIG=/root/.kube/fsel-premium.yaml \
kubectl get nodes
```

```bash
KUBECONFIG=/root/.kube/guruit.yaml \
kubectl get nodes
```

Không tiếp tục nếu một trong các kubeconfig chưa truy cập được cluster.

---

## 4.3. Merge các kubeconfig

Linux: 
```bash
export KUBECONFIG=/root/.kube/fsel-prod.yaml:/root/.kube/fsel-premium.yaml:/root/.kube/guruit.yaml

kubectl config view \
  --merge \
  --flatten \
  > /root/.kube/all-clusters.yaml

```

Windows:
```bash
$env:KUBECONFIG="C:\Users\PHUHM\.kube\fsel-pt-teacher-an4bngw0-kubeconfig;C:\Users\PHUHM\.kube\all-cluster-01.yaml"

kubectl config view `
  --merge `
  --flatten `
  > C:\Users\PHUHM\.kube\all-clusters.yaml

```

Phân quyền:

```bash
chmod 600 /root/.kube/all-clusters.yaml
```

Kiểm tra:

```bash
KUBECONFIG=/root/.kube/all-clusters.yaml \
kubectl config get-contexts
```

Expected:

```text
CURRENT   NAME
          fke-fsel-djtaj383
          fke-fsel-premium-idf94uj8
          guruit
```

---

## 4.4. Đổi tên context

Đổi tên context rõ ràng để dùng lâu dài:

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml
```

```bash
kubectl config rename-context \
  fke-fsel-djtaj383 \
  fsel-prod
```

```bash
kubectl config rename-context \
  fke-fsel-premium-idf94uj8 \
  fsel-premium
```

Kiểm tra:

```bash
kubectl config get-contexts
```

Expected:

```text
CURRENT   NAME
          fsel-prod
          fsel-premium
          guruit
```

---

## 4.5. Kiểm tra từng context

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml
```

```bash
kubectl --context=fsel-prod get nodes
kubectl --context=fsel-premium get nodes
kubectl --context=guruit get nodes
```

Kiểm tra API endpoint:

```bash
kubectl config view \
  --kubeconfig=/root/.kube/all-clusters.yaml \
  --minify=false \
  -o jsonpath='{range .clusters[*]}{.name}{" => "}{.cluster.server}{"\n"}{end}'
```

Expected:

```text
fsel-prod => https://api.djtaj383.prd.m.fke.fptcloud.com
fsel-premium => https://api.idf94uj8.prd.m.fke.fptcloud.com
guruit => https://kube.guruit.vn
```

---

# 5. Login vào Argo CD

## 5.1. Login bằng CLI

```bash
argocd login argocd.example.com \
  --username admin \
  --password '<ARGOCD_PASSWORD>' \
  --grpc-web
```

Nếu Argo CD đang dùng certificate nội bộ:

```bash
argocd login argocd.example.com \
  --username admin \
  --password '<ARGOCD_PASSWORD>' \
  --grpc-web \
  --insecure
```

Không nên dùng `--insecure` lâu dài trong production.

Kiểm tra login:

```bash
argocd account get-user-info
```

---

# 6. Add cluster vào Argo CD

## 6.1. Khai báo kubeconfig tổng

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml
```

Kiểm tra lại context:

```bash
kubectl config get-contexts
```

---

## 6.2. Add cluster fsel-prod

```bash
argocd cluster add fsel-prod \
  --name fsel-prod \
  --yes
```

---

## 6.3. Add cluster fsel-premium

```bash
argocd cluster add fsel-premium \
  --name fsel-premium \
  --yes
```

---

## 6.4. Add cluster guruit

```bash
argocd cluster add guruit \
  --name guruit \
  --yes
```

Argo CD yêu cầu context phải tồn tại trong kubeconfig đang được CLI sử dụng. Lệnh `argocd cluster add` kết nối tới target cluster và tạo các resource cần thiết để Argo CD truy cập cluster.

---

## 6.5. Add cluster bằng kubeconfig cụ thể

Có thể không cần export biến môi trường:

```bash
argocd cluster add fsel-prod \
  --name fsel-prod \
  --kubeconfig /root/.kube/all-clusters.yaml \
  --yes
```

---

## 6.6. Giới hạn namespace được quản lý

Mặc định Argo CD có thể được cấp quyền rộng trên target cluster.

Để chỉ quản lý một số namespace:

```bash
argocd cluster add fsel-prod \
  --name fsel-prod \
  --namespace fsel-prod \
  --namespace monitoring \
  --cluster-resources=false \
  --yes
```

Ý nghĩa:

```text
--namespace
Chỉ định namespace Argo CD được quản lý.

--cluster-resources=false
Không quản lý resource cấp cluster như CRD, ClusterRole,
ClusterRoleBinding và Namespace.
```

Lưu ý:

Một số ứng dụng cần cluster-scoped resource như:

* CRD.
* ClusterRole.
* ClusterRoleBinding.
* StorageClass.
* ClusterIssuer.
* ValidatingWebhookConfiguration.

Với các ứng dụng này, không được tắt `cluster-resources` nếu Argo CD cần trực tiếp quản lý các resource trên.

---

# 7. Kiểm tra cluster đã được add

```bash
argocd cluster list
```

Expected:

```text
SERVER                                            NAME           STATUS
https://kubernetes.default.svc                    in-cluster     Successful
https://api.djtaj383.prd.m.fke.fptcloud.com       fsel-prod      Successful
https://api.idf94uj8.prd.m.fke.fptcloud.com       fsel-premium   Successful
https://kube.guruit.vn                            guruit         Successful
```

Kiểm tra chi tiết:

```bash
argocd cluster get kpi-k8s-uat -o wide
argocd cluster get fsel-premium -o wide
argocd cluster get guruit -o wide
```

Argo CD hỗ trợ `cluster list`, `cluster get`, `cluster add` và `cluster rm` để quản lý cluster credential.

---

# 8. Resource được tạo trên target cluster

Kiểm tra:

```bash
kubectl --context=kpi-k8s-uat \
  -n kube-system get serviceaccount,secret \
  | grep argocd
```

```bash
kubectl --context=fsel-prod \
  get clusterrole,clusterrolebinding \
  | grep argocd
```

Thông thường sẽ có:

```text
serviceaccount/argocd-manager
clusterrole/argocd-manager-role
clusterrolebinding/argocd-manager-role-binding
```

Xem quyền:

```bash
kubectl --context=kpi-k8s-uat \
  get clusterrole argocd-manager-role \
  -o yaml
```

Kiểm tra quyền thực tế:

```bash
kubectl --context=kpi-k8s-uat auth can-i \
  --as=system:serviceaccount:kube-system:argocd-manager \
  get deployments \
  --all-namespaces
```

```bash
kubectl --context=fsel-prod auth can-i \
  --as=system:serviceaccount:kube-system:argocd-manager \
  create deployments \
  -n fsel-prod
```

---

# 9. Cluster Secret trong Argo CD

Argo CD lưu credential của target cluster trong Secret thuộc namespace `argocd`.

Liệt kê:

```bash
kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster
```

Xem cluster name của từng Secret:

```bash
for secret in $(kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster \
  -o name); do

  echo "=== $secret ==="

  kubectl -n argocd get "$secret" \
    -o jsonpath='{.data.name}' \
    | base64 -d

  echo
done
```

Cluster credential Secret được nhận dạng bằng label:

```yaml
argocd.argoproj.io/secret-type: cluster
```

Một Cluster Secret thông thường chứa:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster-fsel-prod
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: fsel-prod
  server: https://api.djtaj383.prd.m.fke.fptcloud.com
  config: |
    {
      "bearerToken": "<SERVICE_ACCOUNT_TOKEN>",
      "tlsClientConfig": {
        "insecure": false,
        "caData": "<BASE64_CA_CERTIFICATE>"
      }
    }
```

Không commit Secret chứa token vào Git repository nếu chưa được mã hóa bằng một cơ chế như:

* Sealed Secrets.
* External Secrets Operator.
* HashiCorp Vault.
* SOPS.

---

# 10. Gắn label cho cluster

## 10.1. Mục đích

ApplicationSet Cluster Generator có thể chọn cluster dựa trên label của Cluster Secret.

Ví dụ:

```text
environment=prod
provider=fpt
region=vn
workload=application
enabled=true
```

Cluster Generator tự động lấy danh sách cluster đã được đăng ký trong Argo CD và cung cấp thông tin cluster dưới dạng parameter cho ApplicationSet.

---

## 10.2. Xác định Secret tương ứng

```bash
kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster \
  -o custom-columns='SECRET:.metadata.name,CLUSTER:.data.name'
```

Do trường `.data.name` đang ở dạng base64, dùng lệnh:

```bash
for secret in $(kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster \
  -o jsonpath='{.items[*].metadata.name}'); do

  name=$(kubectl -n argocd get secret "$secret" \
    -o jsonpath='{.data.name}' | base64 -d)

  server=$(kubectl -n argocd get secret "$secret" \
    -o jsonpath='{.data.server}' | base64 -d)

  echo "$secret | $name | $server"
done
```

---

## 10.3. Gắn label

Giả sử Secret tương ứng là:

```text
cluster-fsel-prod
cluster-fsel-premium
cluster-guruit
```

Gắn label:

```bash
kubectl -n argocd label secret cluster-fsel-prod \
  environment=prod \
  provider=fpt \
  region=vn \
  workload=application \
  enabled=true \
  --overwrite
```

```bash
kubectl -n argocd label secret cluster-fsel-premium \
  environment=prod \
  provider=fpt \
  region=vn \
  workload=premium \
  enabled=true \
  --overwrite
```

```bash
kubectl -n argocd label secret cluster-guruit \
  environment=production \
  provider=private \
  region=vn \
  workload=application \
  enabled=true \
  --overwrite
```

Kiểm tra:

```bash
kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster \
  --show-labels
```

---

# 11. AppProject

## 11.1. Mục đích

AppProject giới hạn:

* Repository được sử dụng.
* Cluster được deploy.
* Namespace được deploy.
* Resource nào được phép tạo.
* Application nào thuộc nhóm quyền nào.

Không nên để toàn bộ ứng dụng chạy bằng project `default`.

---

## 11.2. AppProject mẫu

File:

```text
projects/applications.yaml
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: applications
  namespace: argocd
spec:
  description: Applications deployed to managed Kubernetes clusters

  sourceRepos:
    - https://gitlab.example.com/devops/manifests.git
    - https://gitlab.example.com/devops/helm-charts.git

  destinations:
    - name: fsel-prod
      namespace: fsel-prod

    - name: fsel-premium
      namespace: fsel-premium

    - name: guruit
      namespace: application

  clusterResourceWhitelist:
    - group: ""
      kind: Namespace

    - group: rbac.authorization.k8s.io
      kind: ClusterRole

    - group: rbac.authorization.k8s.io
      kind: ClusterRoleBinding

  namespaceResourceWhitelist:
    - group: "*"
      kind: "*"

  orphanedResources:
    warn: true
```

Apply:

```bash
kubectl apply -f projects/applications.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get appproject applications
```

---

# 12. Git repository structure

Cấu trúc đề xuất:

```text
manifests/
├── applicationsets/
│   ├── services-unstable.yaml
│   ├── services-staging.yaml
│   └── services-prod.yaml
├── projects/
│   └── applications.yaml
├── template/
│   └── stage/
│       ├── base/
│       ├── unstable/
│       ├── staging/
│       └── prod/
└── services/
    ├── auth/
    │   ├── values-unstable.yaml
    │   ├── values-staging.yaml
    │   └── values-prod.yaml
    ├── gateway/
    │   ├── values-unstable.yaml
    │   ├── values-staging.yaml
    │   └── values-prod.yaml
    └── tracking-api/
        ├── values-unstable.yaml
        ├── values-staging.yaml
        └── values-prod.yaml
```

---

# 13. ApplicationSet theo Git Directory Generator

## 13.1. Mục đích

Tự động tạo một Argo CD Application cho mỗi service có file values tương ứng.

Ví dụ:

```text
services/auth/values-prod.yaml
services/gateway/values-prod.yaml
services/tracking-api/values-prod.yaml
```

ApplicationSet sẽ tạo:

```text
auth-prod
gateway-prod
tracking-api-prod
```

---

## 13.2. ApplicationSet cho production

File:

```text
applicationsets/services-prod.yaml
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: services-prod
  namespace: argocd
spec:
  goTemplate: true

  goTemplateOptions:
    - missingkey=error

  generators:
    - git:
        repoURL: https://gitlab.example.com/devops/manifests.git
        revision: main

        files:
          - path: services/*/values-prod.yaml

        requeueAfterSeconds: 60

  template:
    metadata:
      name: '{{ index .path.segments 1 }}-prod'

      labels:
        environment: prod
        managed-by: applicationset

    spec:
      project: applications

      source:
        repoURL: https://gitlab.example.com/devops/manifests.git
        targetRevision: main
        path: template/stage/prod

        helm:
          releaseName: '{{ index .path.segments 1 }}'

          valueFiles:
            - '../../../{{ .path.path }}'

      destination:
        name: fsel-prod
        namespace: fsel-prod

      syncPolicy:
        automated:
          prune: true
          selfHeal: true

        syncOptions:
          - CreateNamespace=true
          - PruneLast=true
          - ApplyOutOfSyncOnly=true

        retry:
          limit: 5

          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m
```

Apply:

```bash
kubectl apply -f applicationsets/services-prod.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get applicationset services-prod
```

```bash
kubectl -n argocd get applications \
  -l environment=prod
```

---

# 14. ApplicationSet theo Cluster Generator

## 14.1. Mục đích

Deploy cùng một ứng dụng tới tất cả cluster phù hợp với label selector.

Ví dụ:

```text
monitoring
external-secrets
cert-manager
logging-agent
node-exporter
```

ApplicationSet Cluster Generator có thể tự động phản ứng khi cluster được thêm hoặc xóa khỏi Argo CD.

---

## 14.2. Template deploy monitoring tới nhiều cluster

File:

```text
applicationsets/monitoring-multi-cluster.yaml
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: monitoring-multi-cluster
  namespace: argocd
spec:
  goTemplate: true

  goTemplateOptions:
    - missingkey=error

  generators:
    - clusters:
        selector:
          matchLabels:
            enabled: "true"
            workload: application

  template:
    metadata:
      name: 'monitoring-{{ .nameNormalized }}'

      labels:
        cluster: '{{ .nameNormalized }}'
        environment: '{{ index .metadata.labels "environment" }}'
        region: '{{ index .metadata.labels "region" }}'

    spec:
      project: applications

      source:
        repoURL: https://gitlab.example.com/devops/manifests.git
        targetRevision: main
        path: platform/monitoring

        helm:
          releaseName: monitoring

          valueFiles:
            - 'values/{{ .name }}.yaml'

      destination:
        server: '{{ .server }}'
        namespace: monitoring

      syncPolicy:
        automated:
          prune: true
          selfHeal: true

        syncOptions:
          - CreateNamespace=true
          - PruneLast=true
```

ApplicationSet Cluster Generator cung cấp các parameter chính:

```text
.name
.nameNormalized
.server
.project
.metadata.labels
.metadata.annotations
```

---

# 15. ApplicationSet kết hợp Git và Cluster Generator

## 15.1. Mục đích

Deploy nhiều service tới nhiều cluster dựa trên:

* File cấu hình trong Git.
* Label của cluster.
* Environment.
* Region.
* Provider.

Sử dụng Matrix Generator để kết hợp:

```text
Git Generator × Cluster Generator
```

---

## 15.2. Matrix ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: services-multi-cluster
  namespace: argocd
spec:
  goTemplate: true

  goTemplateOptions:
    - missingkey=error

  generators:
    - matrix:
        generators:
          - git:
              repoURL: https://gitlab.example.com/devops/manifests.git
              revision: main

              files:
                - path: services/*/values-prod.yaml

          - clusters:
              selector:
                matchLabels:
                  environment: prod
                  enabled: "true"

  template:
    metadata:
      name: '{{ index .path.segments 1 }}-{{ .nameNormalized }}'

      labels:
        application: '{{ index .path.segments 1 }}'
        cluster: '{{ .nameNormalized }}'
        environment: prod

    spec:
      project: applications

      source:
        repoURL: https://gitlab.example.com/devops/manifests.git
        targetRevision: main
        path: template/stage/prod

        helm:
          releaseName: '{{ index .path.segments 1 }}'

          valueFiles:
            - '../../../{{ .path.path }}'
            - '../../../clusters/{{ .name }}/values.yaml'

      destination:
        server: '{{ .server }}'
        namespace: fsel-prod

      syncPolicy:
        automated:
          prune: true
          selfHeal: true

        syncOptions:
          - CreateNamespace=true
          - PruneLast=true
```

Matrix Generator tạo tổ hợp giữa parameter của hai child generators.

Ví dụ:

```text
3 services × 2 clusters = 6 Applications
```

```text
auth-fsel-prod
auth-fsel-premium
gateway-fsel-prod
gateway-fsel-premium
tracking-api-fsel-prod
tracking-api-fsel-premium
```

---

# 16. Chọn cluster theo values file

Có thể khai báo cluster trong từng values file:

```yaml
application:
  name: tracking-api
  environment: prod

destination:
  clusterName: fsel-prod
  namespace: fsel-prod

image:
  repository: registry.example.com/tracking-api
  tag: prod-1.0.0
```

ApplicationSet:

```yaml
destination:
  name: '{{ .destination.clusterName }}'
  namespace: '{{ .destination.namespace }}'
```

Template hoàn chỉnh:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: services
  namespace: argocd
spec:
  goTemplate: true

  goTemplateOptions:
    - missingkey=error

  generators:
    - git:
        repoURL: https://gitlab.example.com/devops/manifests.git
        revision: main

        files:
          - path: services/*/values-*.yaml

        requeueAfterSeconds: 60

  template:
    metadata:
      name: >-
        {{ .application.name }}-{{ .application.environment }}

    spec:
      project: applications

      source:
        repoURL: https://gitlab.example.com/devops/manifests.git
        targetRevision: main
        path: >-
          template/stage/{{ .application.environment }}

        helm:
          releaseName: '{{ .application.name }}'

          valueFiles:
            - '../../../{{ .path.path }}'

      destination:
        name: '{{ .destination.clusterName }}'
        namespace: '{{ .destination.namespace }}'

      syncPolicy:
        automated:
          prune: true
          selfHeal: true

        syncOptions:
          - CreateNamespace=true
```

Ưu điểm:

* Một ApplicationSet quản lý nhiều environment.
* Mỗi service tự chỉ định target cluster.
* Không cần tạo một ApplicationSet cho từng cluster.

Nhược điểm:

* Sai tên cluster trong values sẽ làm Application lỗi.
* Cần kiểm soát values bằng review hoặc schema validation.

---

# 17. Root Application – App of Apps

## 17.1. Mục đích

Root Application quản lý:

* AppProject.
* ApplicationSet.
* Platform component.
* Bootstrap configuration.

File:

```text
bootstrap/root-application.yaml
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: argocd-bootstrap
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://gitlab.example.com/devops/manifests.git
    targetRevision: main
    path: bootstrap/resources

  destination:
    server: https://kubernetes.default.svc
    namespace: argocd

  syncPolicy:
    automated:
      prune: true
      selfHeal: true

    syncOptions:
      - CreateNamespace=true
```

Apply lần đầu:

```bash
kubectl apply -f bootstrap/root-application.yaml
```

Sau đó các thay đổi tiếp theo được quản lý qua GitOps.

---

# 18. Webhook GitLab

## 18.1. Mục đích

Mặc định Argo CD poll Git repository theo chu kỳ.

Webhook giúp Argo CD refresh Application ngay khi có commit mới.

Webhook endpoint:

```text
https://argocd.example.com/api/webhook
```

Trong GitLab:

```text
Project
→ Settings
→ Webhooks
```

Cấu hình:

```text
URL:
https://argocd.example.com/api/webhook

Trigger:
Push events
Tag push events
Merge request events nếu cần
```

Nếu dùng webhook secret, cấu hình vào:

```text
argocd-secret
```

Kiểm tra log:

```bash
kubectl -n argocd logs deploy/argocd-server \
  --since=10m \
  | grep -i webhook
```

Webhook chỉ kích hoạt refresh trạng thái Git.

Application vẫn cần:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

để tự động sync.

---

# 19. Network requirement

## 19.1. Luồng bắt buộc

```text
argocd-application-controller
        |
        | TCP 443 hoặc 6443
        v
Target Kubernetes API Server
```

Không chỉ máy chạy Argo CD CLI cần kết nối được target cluster.

Pod `argocd-application-controller` cũng phải kết nối được target API Server.

---

## 19.2. Test từ Argo CD controller

Lấy pod:

```bash
CONTROLLER_POD=$(kubectl -n argocd get pod \
  -l app.kubernetes.io/name=argocd-application-controller \
  -o jsonpath='{.items[0].metadata.name}')
```

Test DNS:

```bash
kubectl -n argocd exec "$CONTROLLER_POD" -- \
  getent hosts api.djtaj383.prd.m.fke.fptcloud.com
```

Test API:

```bash
kubectl -n argocd exec "$CONTROLLER_POD" -- \
  wget -S -O- \
  --no-check-certificate \
  https://api.djtaj383.prd.m.fke.fptcloud.com/version
```

Nếu container không có `wget`, tạo debug pod:

```bash
kubectl -n argocd run network-debug \
  --image=nicolaka/netshoot \
  --restart=Never \
  -- sleep 3600
```

```bash
kubectl -n argocd exec -it network-debug -- bash
```

Trong debug pod:

```bash
dig api.djtaj383.prd.m.fke.fptcloud.com
nc -vz api.djtaj383.prd.m.fke.fptcloud.com 443
curl -vk https://api.djtaj383.prd.m.fke.fptcloud.com/version
```

Xóa debug pod:

```bash
kubectl -n argocd delete pod network-debug
```

---

# 20. TLS và certificate

## 20.1. Yêu cầu

Hostname trong kubeconfig phải khớp với SAN của API Server certificate.

Ví dụ:

```yaml
server: https://kube.guruit.vn
```

Certificate phải có:

```text
DNS:kube.guruit.vn
```

Kiểm tra:

```bash
openssl s_client \
  -connect kube.guruit.vn:443 \
  -servername kube.guruit.vn \
  </dev/null 2>/dev/null \
  | openssl x509 \
      -noout \
      -subject \
      -issuer \
      -dates \
      -ext subjectAltName
```

Không sử dụng certificate của Ingress Controller để đại diện cho Kubernetes API nếu endpoint thực tế không được proxy đúng ở TCP layer.

Các lỗi thường gặp:

```text
x509: certificate is valid for 10.96.0.1, 10.10.0.182,
not kube.guruit.vn
```

```text
x509: certificate signed by unknown authority
```

```text
Kubernetes Ingress Controller Fake Certificate
```

---

## 20.2. Không dùng insecure nếu không bắt buộc

Có thể add cluster bằng:

```bash
argocd cluster add guruit \
  --name guruit \
  --insecure \
  --yes
```

Nhưng đây chỉ nên là workaround tạm thời.

Fix chuẩn:

* API endpoint dùng đúng hostname.
* Certificate có đúng SAN.
* Kubeconfig có đúng CA certificate.
* Argo CD controller trust CA đó.

---

# 21. Security

## 21.1. Không commit kubeconfig

Kubeconfig có thể chứa:

* Bearer token.
* Client certificate.
* Client private key.
* Cloud access credential.
* Exec authentication command.

Thêm vào `.gitignore`:

```gitignore
*.kubeconfig
all-clusters.yaml
kubeconfig/
```

---

## 21.2. Không dùng admin kubeconfig làm credential runtime

Kubeconfig admin chỉ nên dùng để chạy:

```bash
argocd cluster add
```

Sau đó Argo CD sử dụng ServiceAccount riêng.

Kiểm tra:

```bash
kubectl --context=fsel-prod \
  -n kube-system get serviceaccount argocd-manager
```

---

## 21.3. Tách production và non-production

Mô hình an toàn hơn:

```text
Argo CD Non-Production
├── DEV
├── QA
└── STAGING

Argo CD Production
├── PROD FPT
├── PROD Premium
└── PROD Private Cloud
```

Nguyên nhân:

Một Argo CD giữ credential tới tất cả cluster mà nó quản lý.

Nếu Argo CD bị compromise, attacker có thể sử dụng các credential này để tác động tới target cluster.

---

## 21.4. Backup Argo CD

Các resource cần backup:

```text
Application
ApplicationSet
AppProject
Repository Secret
Cluster Secret
argocd-cm
argocd-rbac-cm
argocd-secret
```

Backup:

```bash
kubectl -n argocd get application \
  -o yaml > backup-applications.yaml
```

```bash
kubectl -n argocd get applicationset \
  -o yaml > backup-applicationsets.yaml
```

```bash
kubectl -n argocd get appproject \
  -o yaml > backup-appprojects.yaml
```

```bash
kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster \
  -o yaml > backup-clusters.yaml
```

File backup Secret phải được mã hóa và giới hạn quyền truy cập.

---

# 22. Verify toàn bộ hệ thống

## 22.1. Kiểm tra kubeconfig

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml

kubectl config get-contexts
```

```bash
kubectl --context=fsel-prod get nodes
kubectl --context=fsel-premium get nodes
kubectl --context=guruit get nodes
```

---

## 22.2. Kiểm tra Argo CD cluster

```bash
argocd cluster list
```

Expected:

```text
STATUS: Successful
```

---

## 22.3. Kiểm tra ApplicationSet

```bash
kubectl -n argocd get applicationset
```

```bash
kubectl -n argocd describe applicationset services-prod
```

---

## 22.4. Kiểm tra Application được generate

```bash
kubectl -n argocd get applications
```

Hoặc:

```bash
argocd app list
```

---

## 22.5. Kiểm tra trạng thái sync

```bash
argocd app get tracking-api-prod
```

Expected:

```text
Sync Status: Synced
Health Status: Healthy
```

---

## 22.6. Kiểm tra resource trên đúng cluster

```bash
kubectl --context=fsel-prod \
  -n fsel-prod get deployment,pod,service
```

Đồng thời bảo đảm resource không xuất hiện nhầm cluster:

```bash
kubectl --context=fsel-premium \
  -n fsel-prod get deployment tracking-api
```

Expected:

```text
Error from server (NotFound)
```

nếu ứng dụng chỉ được deploy vào `fsel-prod`.

---

# 23. Test Application đơn giản

Tạo file:

```text
test-application.yaml
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook-fsel-prod
  namespace: argocd
spec:
  project: applications

  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook

  destination:
    name: fsel-prod
    namespace: argocd-test

  syncPolicy:
    automated:
      prune: true
      selfHeal: true

    syncOptions:
      - CreateNamespace=true
```

Apply:

```bash
kubectl apply -f test-application.yaml
```

Theo dõi:

```bash
argocd app get guestbook-fsel-prod
```

Kiểm tra target cluster:

```bash
kubectl --context=fsel-prod \
  -n argocd-test get all
```

Xóa test:

```bash
kubectl -n argocd delete application guestbook-fsel-prod
```

Nếu finalizer được cấu hình, Argo CD có thể xóa resource trên target cluster cùng Application.

---

# 24. Troubleshooting

## Problem: Context không tồn tại

### Evidence

```text
Context <name> does not exist in kubeconfig
```

### Fix

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml

kubectl config get-contexts
```

Sử dụng chính xác tên context:

```bash
argocd cluster add fsel-prod \
  --name fsel-prod
```

---

## Problem: Argo CD cluster status Unknown

### Evidence

```bash
argocd cluster list
```

```text
STATUS: Unknown
```

### Cause

Thường do:

* Argo CD controller không kết nối được API Server.
* DNS không resolve.
* Firewall chặn.
* Certificate không hợp lệ.
* ServiceAccount token không hợp lệ.

### Fix

```bash
kubectl -n argocd logs statefulset/argocd-application-controller \
  --since=15m \
  | grep -iE 'error|cluster|tls|x509|timeout'
```

Test từ namespace Argo CD:

```bash
kubectl -n argocd run network-debug \
  --image=nicolaka/netshoot \
  --restart=Never \
  -- sleep 3600
```

```bash
kubectl -n argocd exec network-debug -- \
  curl -vk https://<TARGET-API>/version
```

---

## Problem: Certificate signed by unknown authority

### Evidence

```text
x509: certificate signed by unknown authority
```

### Cause

CA trong Cluster Secret không khớp CA ký API Server certificate.

### Fix

Kiểm tra CA trong kubeconfig nguồn:

```bash
kubectl config view \
  --kubeconfig=/root/.kube/all-clusters.yaml \
  --raw \
  -o yaml
```

Kiểm tra certificate server:

```bash
openssl s_client \
  -connect kube.guruit.vn:443 \
  -servername kube.guruit.vn \
  -showcerts
```

Sau khi sửa kubeconfig, remove và add lại cluster:

```bash
argocd cluster rm guruit
```

```bash
argocd cluster add guruit \
  --name guruit \
  --kubeconfig /root/.kube/all-clusters.yaml \
  --yes
```

---

## Problem: Certificate SAN mismatch

### Evidence

```text
x509: certificate is valid for 10.96.0.1, 10.10.0.182,
not kube.guruit.vn
```

### Cause

Hostname trong kubeconfig không nằm trong SAN của Kubernetes API certificate.

### Fix

Chọn một trong các cách:

1. Cấp lại API Server certificate có SAN `kube.guruit.vn`.
2. Dùng endpoint đã tồn tại trong SAN.
3. Đặt TCP Load Balancer trước API Server nhưng giữ certificate đúng hostname.
4. Cập nhật kubeconfig dùng đúng API endpoint.

Không dùng HTTP Ingress thông thường để proxy Kubernetes API.

---

## Problem: ApplicationSet không tạo Application

### Evidence

```bash
kubectl -n argocd get applicationset
```

ApplicationSet tồn tại nhưng không có Application được tạo.

### Cause

Thường do:

* Git file pattern không match.
* Cluster label selector không match.
* `missingkey=error` phát hiện field không tồn tại.
* Repo credential sai.
* Template render lỗi.

### Fix

```bash
kubectl -n argocd describe applicationset <NAME>
```

```bash
kubectl -n argocd logs deploy/argocd-applicationset-controller \
  --since=15m
```

Kiểm tra file path:

```bash
find services -name 'values-prod.yaml'
```

Kiểm tra cluster label:

```bash
kubectl -n argocd get secret \
  -l 'argocd.argoproj.io/secret-type=cluster,environment=prod' \
  --show-labels
```

---

## Problem: Application bị InvalidSpecError

### Evidence

```text
InvalidSpecError
cluster not found
```

### Cause

`destination.name` không trùng với tên cluster trong Argo CD.

### Fix

```bash
argocd cluster list
```

Sửa:

```yaml
destination:
  name: fsel-prod
```

Không sử dụng Kubernetes context name cũ nếu cluster đã được đăng ký bằng tên khác.

---

## Problem: Permission denied

### Evidence

```text
permission denied
```

```text
forbidden: User system:serviceaccount:kube-system:argocd-manager
cannot create resource
```

### Cause

ServiceAccount Argo CD thiếu quyền với resource hoặc namespace.

### Fix

Kiểm tra:

```bash
kubectl --context=fsel-prod auth can-i \
  --as=system:serviceaccount:kube-system:argocd-manager \
  create deployments \
  -n fsel-prod
```

Kiểm tra ClusterRole:

```bash
kubectl --context=fsel-prod \
  get clusterrole argocd-manager-role \
  -o yaml
```

Sau đó bổ sung đúng quyền cần thiết.

Không thêm `cluster-admin` trước khi xác định resource bị thiếu quyền.

---

## Problem: Cluster đã xóa nhưng Application vẫn còn

### Evidence

Cluster không còn trong Argo CD nhưng Application vẫn tồn tại hoặc báo destination unavailable.

### Fix

Kiểm tra ApplicationSet:

```bash
kubectl -n argocd get applicationset <NAME> -o yaml
```

Kiểm tra Application owner:

```bash
kubectl -n argocd get application <APP> \
  -o jsonpath='{.metadata.ownerReferences}'
```

Nếu Application không còn thuộc ApplicationSet, xóa thủ công:

```bash
kubectl -n argocd delete application <APP>
```

Cẩn thận với finalizer vì thao tác có thể xóa resource trên target cluster.

---

# 25. Remove cluster

Trước khi remove cluster, kiểm tra Application đang sử dụng cluster:

```bash
argocd app list \
  -o wide \
  | grep fsel-prod
```

Remove:

```bash
argocd cluster rm fsel-prod
```

Kiểm tra:

```bash
argocd cluster list
```

Xóa ServiceAccount trên target nếu không còn sử dụng:

```bash
kubectl --context=fsel-prod \
  -n kube-system delete serviceaccount argocd-manager
```

```bash
kubectl --context=fsel-prod \
  delete clusterrole argocd-manager-role
```

```bash
kubectl --context=fsel-prod \
  delete clusterrolebinding argocd-manager-role-binding
```

Không xóa trước khi chắc chắn cluster không còn Application nào đang được Argo CD quản lý.

---

# 26. Quy trình thêm cluster mới

## Step 1: Nhận kubeconfig

```bash
chmod 600 new-cluster.yaml
```

## Step 2: Test kubeconfig

```bash
KUBECONFIG=new-cluster.yaml kubectl get nodes
```

## Step 3: Merge kubeconfig

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml:new-cluster.yaml

kubectl config view \
  --merge \
  --flatten \
  > /root/.kube/all-clusters-new.yaml
```

```bash
mv /root/.kube/all-clusters-new.yaml \
  /root/.kube/all-clusters.yaml

chmod 600 /root/.kube/all-clusters.yaml
```

## Step 4: Rename context

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml

kubectl config rename-context \
  <OLD_CONTEXT> \
  <NEW_CONTEXT>
```

## Step 5: Add vào Argo CD

```bash
argocd cluster add <NEW_CONTEXT> \
  --name <NEW_CLUSTER_NAME> \
  --yes
```

## Step 6: Gắn label

```bash
kubectl -n argocd label secret <CLUSTER_SECRET> \
  environment=prod \
  provider=<PROVIDER> \
  region=<REGION> \
  enabled=true \
  --overwrite
```

## Step 7: Kiểm tra ApplicationSet

```bash
kubectl -n argocd get applicationset
kubectl -n argocd get applications
```

## Step 8: Test deployment

```bash
argocd app get <APPLICATION_NAME>
```

```bash
kubectl --context=<NEW_CONTEXT> \
  -n <NAMESPACE> get all
```

---

# 27. Checklist

## Kubeconfig

* [ ] Mỗi kubeconfig truy cập được cluster.
* [ ] Các kubeconfig đã được merge.
* [ ] Context được đổi tên rõ ràng.
* [ ] File có permission `600`.
* [ ] Kubeconfig không được commit lên Git.
* [ ] API endpoint có certificate hợp lệ.

## Argo CD

* [ ] Login Argo CD CLI thành công.
* [ ] Tất cả cluster có status `Successful`.
* [ ] Cluster Secret tồn tại.
* [ ] Cluster Secret có label đúng.
* [ ] Application Controller kết nối được API Server.
* [ ] Repository credential hoạt động.

## RBAC

* [ ] `argocd-manager` ServiceAccount tồn tại.
* [ ] RBAC đúng với namespace cần deploy.
* [ ] Cluster-scoped permission chỉ được cấp khi cần.
* [ ] AppProject giới hạn đúng destination.
* [ ] Production không sử dụng project `default`.

## ApplicationSet

* [ ] Git pattern match đúng file.
* [ ] Cluster selector match đúng label.
* [ ] `destination.name` hoặc `destination.server` đúng.
* [ ] Application được generate.
* [ ] Application ở trạng thái `Synced`.
* [ ] Application ở trạng thái `Healthy`.
* [ ] Resource xuất hiện đúng target cluster.
* [ ] Resource không xuất hiện nhầm cluster.

---

# 28. Lệnh kiểm tra nhanh

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml
```

```bash
kubectl config get-contexts
```

```bash
for context in fsel-prod fsel-premium guruit; do
  echo "=== $context ==="
  kubectl --context="$context" get nodes
done
```

```bash
argocd cluster list
```

```bash
kubectl -n argocd get secret \
  -l argocd.argoproj.io/secret-type=cluster \
  --show-labels
```

```bash
kubectl -n argocd get appproject
```

```bash
kubectl -n argocd get applicationset
```

```bash
argocd app list
```

```bash
kubectl -n argocd logs statefulset/argocd-application-controller \
  --since=10m \
  | grep -iE 'error|warning|timeout|x509|forbidden'
```

---

# 29. Reference

* Argo CD Cluster Management: `argocd cluster add` sử dụng context trong kubeconfig và tạo các resource cần thiết trên target cluster.
* Argo CD Cluster Command Reference: quản lý cluster bằng `add`, `get`, `list` và `rm`.
* ApplicationSet Cluster Generator: tự động lấy danh sách cluster đã đăng ký và đưa thông tin cluster vào template.
* Cluster Bootstrapping: Argo CD khuyến nghị ApplicationSet Cluster Generator cho các trường hợp bootstrap và triển khai ứng dụng tới cluster mới.
* Matrix Generator: kết hợp parameter từ hai generator để tạo các tổ hợp Application.


# 30. Tạo app trên argocd

argocd app create fsel-prod-network `
  --repo https://gitlab.fsel.edu.vn/devops/argocd-deploy.git `
  --revision main `
  --path values/operation/fsel-prod/network `
  --values values.yaml `
  --dest-server https://kubernetes.default.svc `
  --dest-namespace network `
  --project default `
  --sync-option CreateNamespace=true