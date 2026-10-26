---
name: "Sửa key Secret không lộ giá trị"
description: "Sửa một key trong Kubernetes Secret bằng kubectl patch mà không in giá trị ra chat, kèm kiểm độ dài sau khi sửa."
group: "DevOps"
origin: javis-learned
status: active
created: 2026-10-26
---
## Khi nào dùng
- Cần đổi một key trong Kubernetes Secret (cookie-secret, khối cấu hình kubeconfig như tls-server-name, mật khẩu) mà giá trị không được lọt vào chat.
- App lỗi vì giá trị secret sai: độ dài không đúng, hoặc thiếu một dòng cấu hình trong file secret.

## Chuẩn bị
- Xác định context và namespace trước. Nếu chưa rõ thì hỏi người dùng.
- Đây là lệnh ghi lên cluster. Chỉ chạy khi người dùng đã đồng ý đổi secret trên cluster đó.

## Cách chạy
1. Đọc key cần sửa và đo độ dài, không in giá trị: `kubectl --context <ctx> -n <ns> get secret <name> -o jsonpath='{.data.<key>}'`, rồi decode base64 và đếm ký tự.
2. Dựng giá trị mới ngay trong bộ nhớ của lệnh, không ghi ra file tạm có thể bị commit.
3. Ghi lại bằng merge patch: `kubectl ... patch secret <name> --type merge -p <payload>`. Payload là JSON có khoá `data` với giá trị base64 mới.
4. Đo lại độ dài sau khi patch. Nếu app chỉ đọc secret lúc khởi động thì xoá pod để nó nạp lại.

## Bẫy
- Trong PowerShell, JSON viết trong nháy đơn kèm dấu gạch chéo trước nháy kép sẽ giữ nguyên dấu gạch chéo và làm hỏng payload. Dựng payload bằng `ConvertTo-Json` hoặc here-string rồi truyền vào `-p`.
- `data` cần base64 sẵn. `stringData` nhận chuỗi thường. Đừng trộn hai kiểu trong cùng một payload.
- Không in giá trị secret ra chat trừ khi người dùng yêu cầu rõ. Báo độ dài và kiểu thay thế.
- Đừng xoá pod theo label selector đoán mò. Lấy tên pod từ `get pods` trước.
- Sau khi sửa secret trên cluster, sửa luôn file secret nguồn ở máy local (file đã gitignore). Nếu không, lần apply sau sẽ ghi đè giá trị cũ.

## Kiểm chứng
- Đo lại độ dài giá trị trên cluster, phải đúng số đã kỳ vọng.
- Pod mới Ready và log không còn lỗi liên quan đến key vừa sửa.
