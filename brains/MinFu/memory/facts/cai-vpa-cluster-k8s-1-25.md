---
type: business
provenance: user
origin: javis-learned
created: 2026-10-08
updated: 2026-10-08
---
- Ngày 2026-10-08, người dùng hỏi về VPA cho một cluster Kubernetes 1.25. Chưa xác định đó là context nào trong 7 context đang quản lý.
- Bản VPA đã clone (release 1.1.1): `D:\private01\autoscaler-vpa-1.1.1`. Script cài nằm tại `vertical-pod-autoscaler\hack\vpa-up.sh`, không nằm ở thư mục gốc.
- Người dùng chạy script bằng Git Bash trên Windows.
- Trạng thái thực tế tính đến 2026-10-08 (đọc từ log người dùng gửi): CRD, RBAC, `vpa-recommender` và `vpa-updater` đã được tạo. Chứng chỉ của `vpa-admission-controller` bị lỗi vì Git Bash đổi `/CN=vpa_webhook_ca` thành `C:/Program Files/Git/CN=vpa_webhook_ca`.
- Chưa xác minh việc chạy lại `gencerts.sh` đã thành công hay chưa.
- Hướng người dùng đang cân nhắc (mục tiêu, chưa chốt): giữ số replica cố định, dùng VPA để tự chỉnh `resources.requests` sao cho tối ưu tài nguyên mà vẫn chịu được tải khi số user tăng.
- Lưu ý: câu trả lời trong phiên cho rằng `minAllowed`/`maxAllowed` phải trùng requests/limits của Pod là KHÔNG đúng và chưa được đính chính với người dùng (minAllowed/maxAllowed là biên cho recommendation, không phải bản sao requests/limits).

Liên quan: [[ho-so-devops-va-he-thong]], [[kubectl-context-va-quyen-kiem-tra]]
