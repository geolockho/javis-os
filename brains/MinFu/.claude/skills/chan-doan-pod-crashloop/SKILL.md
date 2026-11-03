---
name: Chẩn đoán pod CrashLoopBackOff
description: Tìm nguyên nhân pod Kubernetes CrashLoopBackOff qua log container đã chết, secret, quyền volume và kết nối DB, chỉ dùng lệnh đọc.
group: DevOps
origin: javis-learned
status: active
created: 2026-10-26
updated: '2026-10-26'
learned_updated: '2026-10-26'
---
## Khi nào dùng
- Pod báo CrashLoopBackOff, 0/N Ready, hoặc ReplicaSet mới không lên Ready sau khi deploy.
- Có nhiều ReplicaSet cùng crash, cần biết bản nào đang chạy.

## Chuẩn bị
- Xác định context và namespace trước (`kubectl config get-contexts`). Nếu chưa rõ thì hỏi người dùng.
- Chỉ dùng lệnh đọc: get, describe, logs, auth can-i. Lệnh ghi như patch, apply, hoặc exec tạo role chỉ chạy khi người dùng đồng ý.

## Quy trình
1. Xem pod và ReplicaSet: `kubectl --context <ctx> -n <ns> get pods -o wide` và `get rs`, để biết bản nào mới, bản nào cũ.
2. Xem container nào chết: `kubectl describe pod <pod>`, đọc Last State, Exit Code và Events.
3. Đọc log lần chết gần nhất: `kubectl logs <pod> -c <container> --previous`. Làm lần lượt từng container, vì một pod có thể có cả app lẫn sidecar.
4. Phân loại theo thông báo lỗi:
   - `password authentication failed`: role hoặc DB chưa tồn tại trên Postgres, hoặc mật khẩu lệch. Kiểm bằng `\du` và `\l` qua exec psql trước khi kết luận là sai mật khẩu.
   - `Permission denied` khi đọc file trong volume: xem securityContext, fsGroup và defaultMode của volume.
   - `cookie_secret ... but is N bytes` từ oauth2-proxy: secret phải đúng 16, 24 hoặc 32 byte. Đo độ dài sau khi decode base64, không đoán từ nhìn.
   - Lỗi định dạng hoặc độ dài của secret khác: đo độ dài, không in giá trị.
5. Sau khi sửa: `kubectl rollout status deploy/<name>`, rồi xem lại pod.

## Bẫy
- Không in giá trị secret ra chat. Chỉ báo độ dài và kiểu, ví dụ 44 ký tự base64 chuẩn.
- Pod ImagePullBackOff do tag không còn trên registry là pod rác của bản cũ, không phải lỗi của bản mới.
- defaultMode trong JSON patch phải là số thập phân: 0440 tương ứng 288.
- fsGroup cấp group cho mọi container trong pod, không chỉ container mount volume.
- Chuỗi hex 64 ký tự là 64 byte, oauth2-proxy từ chối. Chuỗi hex 32 ký tự là 32 byte, đúng.
- Repo GitOps có image-updater tự commit: git pull --rebase trước khi push.

## Kiểm chứng
- Pod đủ N/N Ready và không restart thêm sau khi rollout xong. Ghi rõ lệnh nào đã chạy và kết quả.

## Lịch sử (tự học)
- [2026-10-26] Ca thật ngày 2026-10-26 trên fsel-local: oauth2-proxy CrashLoop vì cookie_secret dài 64 byte, bước phân loại cũ không có dòng này nên dễ bỏ sót. Đã thêm dòng phân loại và bẫy độ dài hex, giữ nguyên phần còn đúng.
