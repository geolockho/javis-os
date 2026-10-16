---
type: fact
provenance: user
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---

# Hồ sơ DevOps và các hệ thống đang quản lý

**Nguồn:** Tin nhắn trực tiếp của người dùng qua Telegram, chat_id `1110969232`, ngày 2026-10-07 lúc 09:09 và bản cập nhật lúc 09:15 (Asia/Ho_Chi_Minh). Người dùng yêu cầu ghi nhớ thông tin này. Nguyên văn được lưu ở mục "Tin nhắn nguồn" bên dưới.

**Trạng thái:** Thông tin do người dùng xác nhận tại thời điểm 2026-10-07; chưa kiểm tra độc lập kiến trúc hay trạng thái vận hành của các hệ thống.

## Hồ sơ

- Nghề nghiệp: DevOps.
- Kinh nghiệm: 3 năm, tính theo lời người dùng ngày 2026-10-07.
- Năm sinh: 1995.
- Giới tính: nam.

## Các hệ thống đang quản lý

- **Fsel-prod:** client -> DNS (Cloudflare) -> FW -> LB -> K8s (Ingress -> Service -> Pod).
- **Fsel-pt-teacher:** người dùng mô tả "mô hình tương tự fsel-prod"; chưa xác nhận mọi thành phần hoặc cấu hình giống hệt.
- **Fsel-local:** client -> DNS (Cloudflare) -> Router (MikroTik) -> K8s (MetalLB -> Ingress -> Service -> Pod).
- **guruit**, **kpi**, **kpi-uat**, **lhp-k8s:** người dùng xác nhận đang quản lý; mô hình triển khai được bổ sung bên dưới, chưa có luồng truy cập chi tiết.

## Nơi triển khai và mô hình cluster

Theo bản cập nhật của người dùng ngày 2026-10-07 lúc 09:15:

- **fsel-prod**, **fsel-pt-teacher:** sử dụng cloud trong nước là **FPT Cloud**, dịch vụ **FKE**. Chưa có thông tin về số master/control-plane của hai hệ thống này.
- **lhp-k8s**, **guruit**, **kpi**, **kpi-uat**, **fsel-local:** triển khai **on-prem**.
- **kpi:** mô hình **multi-cluster**; chưa có thông tin về số cluster và số master của từng cluster.
- **lhp-k8s**, **guruit**, **kpi-uat**, **fsel-local:** mỗi hệ thống **1 master**. Phạm vi "còn lại là 1 master" được hiểu theo nhóm on-prem vừa nêu, ngoại trừ kpi; không suy ra số worker hoặc áp dụng cho FKE.

**Áp dụng:** Dùng hồ sơ này làm ngữ cảnh khi trao đổi về DevOps và các hệ thống của người dùng. Không tự suy ra phiên bản, IP, tài khoản, cấu hình hay tình trạng live. Khi cần thông tin hiện tại, phải kiểm tra nguồn phù hợp hoặc hỏi người dùng. Không tự tăng số năm kinh nghiệm từ ngày lưu.

## Tin nhắn nguồn

### Hồ sơ và luồng truy cập, 09:09

> Nhớ thông tin về t: T là DevOps, 3 năm kinh nghiệm, sinh năm 1995, nam. Các hệ thống đang quản lý:
> Fsel-prod: client -> DNS (cloudflare) > FW > LB > K8s (ingress > Service > Pod)
> Fsel-pt-teacher: mô hình tương tự fsel-prod
> Fsel-local: client > DNS(cloudflare) > Router (Mikrotik) > K8s (metallb > Ingress > service > pod)
> Ngoài ra còn có: guruit, kpi, kpi-uat, lhp-k8s

### Nơi triển khai và mô hình cluster, 09:15

> cập nhật bộ nhớ: fsel-prod,fsel-pt-teacher sử dụng cloud trong nước, là fpt cloud, và sử dụng dịch vụ fke. lhp-k8s, guruit, kpi,kpi-uat, fsel-local là onprem, riêng kpi sử dụng mô hình multi-cluster, còn lại là 1 master
