---
name: "Quét secret trước commit"
description: "Quét các file đã stage tìm cert, private key, JWT, token dài và Slack webhook trước khi commit repo."
group: "DevOps"
origin: javis-learned
status: active
created: 2026-10-26
---
## Khi nào dùng
- Trước khi commit hoặc push một repo có file cấu hình chứa secret (cert, token, kubeconfig).
- Khi người dùng hỏi có secret nào lọt vào commit không.

## Chuẩn bị
- Đứng trong thư mục repo git.
- Biết các file secret cần chặn, ví dụ deploy/secret.yaml và thư mục secrets/.

## Cách chạy
1. Kiểm từng file secret đã bị ignore: git check-ignore cho đường dẫn của file.
2. Xem danh sách file sắp commit: git status, rồi git diff --cached --stat.
3. Quét nội dung đã stage tìm: BEGIN PRIVATE KEY, BEGIN CERTIFICATE, JWT (bắt đầu bằng eyJ), token dài không phải JWT, hooks.slack.com/services.
4. Báo kết quả: liệt kê file nghi ngờ, không in giá trị secret ra chat.

## Bẫy
- Xoá secret khỏi file sau khi đã commit là chưa đủ, lịch sử git vẫn còn. Coi như đã lộ và phải đổi (rotate) secret.
- Chỉ quét file đã stage, không quét file chưa add.

## Kiểm chứng
- git check-ignore trả về đường dẫn của mọi file secret.
- Lần quét không còn kết quả nghi ngờ.
