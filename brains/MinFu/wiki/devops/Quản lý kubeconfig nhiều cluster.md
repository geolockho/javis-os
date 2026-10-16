---
type: wiki
status: active
tags: [wiki, devops]
created: 2026-10-07
updated: 2026-10-07
aliases: ["KUBECONFIG", "Merged kubeconfig", "Kubernetes contexts"]
source: "[[sources/readme/argocd-cluster-manager]]"
---

# Quản lý kubeconfig nhiều cluster

Kubeconfig nhiều cluster tập hợp cấu hình để kubectl và Argo CD CLI chọn đúng API target. Trang này tổng hợp runbook Argo CD và certificate, không phải kiểm kê cấu hình live. [[sources/readme/argocd-cluster-manager]] [[sources/readme/kuberntes-certificate-renew]]

## Context và tên đăng ký

Context local là đầu vào `cluster add`; tên đăng ký bằng `--name` là tên `Application.spec.destination.name`. Với `cluster not found`, đối chiếu `argocd cluster list`, không mặc định dùng context cũ. [[sources/readme/argocd-cluster-manager]]

## Merge đúng file

Nguồn dùng `:` giữa các file KUBECONFIG trên Linux, `;` trên Windows. Kiểm tra từng file, xuất file merge mới bằng `config view --merge --flatten`, rồi kiểm tra context và kết nối trước khi thay bản cũ; Linux đặt permission `600`. [[sources/readme/argocd-cluster-manager]]

Mẫu Linux theo nguồn, cần thay đường dẫn thực tế: [[sources/readme/argocd-cluster-manager]]

```bash
export KUBECONFIG=/root/.kube/all-clusters.yaml:new-cluster.yaml
kubectl config view --merge --flatten > /root/.kube/all-clusters-new.yaml
kubectl --kubeconfig=/root/.kube/all-clusters-new.yaml config get-contexts
kubectl --kubeconfig=/root/.kube/all-clusters-new.yaml --context=<CONTEXT> get nodes
```

Nguồn có `rename-context` để tên rõ ràng. Mẫu merge không có `--raw`, khác các lệnh trích certificate; cần kiểm tra credential trong file đầu ra usable bằng kết nối thực tế, chưa coi mẫu này đã được kiểm chứng trên host. [[sources/readme/argocd-cluster-manager]] [[sources/readme/kuberntes-certificate-renew]]

## Credential và cập nhật

Kubeconfig có thể chứa token, certificate/private key hoặc exec credential. Nguồn yêu cầu loại file thật khỏi Git bằng `.gitignore`, không dùng admin kubeconfig làm credential runtime Argo CD. [[sources/readme/argocd-cluster-manager]]

Renew `/etc/kubernetes/admin.conf` không tự cập nhật bản đã copy. Với file nhiều context, không copy đè toàn file; cập nhật đúng credential/context và đúng file mà KUBECONFIG đang dùng. [[sources/readme/kuberntes-certificate-renew]]

Liên quan: [[Argo CD đa cluster]], [[Gia hạn certificate kubeconfig bằng kubeadm]], [[Kubeconfig ServiceAccount cho FPT FKE]].
