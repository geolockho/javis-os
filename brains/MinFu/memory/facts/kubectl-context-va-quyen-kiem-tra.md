---
type: preference
provenance: user
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---

# Kubectl context và quyền kiểm tra lỗi

## Các context người dùng quản lý

Người dùng xác nhận quản lý 7 context: `fsel-local`, `fsel-prod`, `fsel-pt-teacher`, `guruit`, `kpi`, `kpi-uat`, `lhp-k8s`.

**Nguồn xác nhận:** Tin nhắn Telegram của người dùng, chat_id `1110969232`, ngày 2026-10-07 lúc 09:11 (Asia/Ho_Chi_Minh), sau khi Javis liệt kê các context bằng `kubectl config get-contexts`:

> lưu vào bộ nhớ: t đang quản lý những context này, m có thể tự chuyển context để check lỗi khi t yêu cầu

**Bằng chứng local:** Lượt trước trong cùng cuộc hội thoại, `kubectl config get-contexts` chạy thành công (exit_code: 0) trên host hiện tại, trả về đúng 7 tên trên. Context được chọn tại lần kiểm tra đó là `kpi-uat`, namespace `default`. Đây là ảnh chụp trạng thái cấu hình local, không xác nhận kết nối hoặc sức khỏe cluster, không thay thế dữ liệu live ở lượt sau.

## Quyền người dùng đã cấp

- Khi người dùng yêu cầu kiểm tra lỗi, Javis được tự chọn hoặc chuyển sang context tương ứng với hệ thống được yêu cầu, không cần xin lại quyền chuyển context.
- Ưu tiên chỉ định `kubectl --context=<context>` cho từng lệnh để chọn đúng cluster và tránh ảnh hưởng context mặc định của phiên khác. Có thể dùng `kubectl config use-context` khi việc kiểm tra cần chuyển context mặc định.
- Áp dụng quyền này cho việc chẩn đoán: đọc trạng thái, events, logs và cấu hình liên quan. Tin nhắn này không tự cấp quyền sửa, xóa hoặc triển khai tài nguyên cluster; những thao tác đó theo yêu cầu và phạm vi được người dùng giao ở từng task.
- Nếu chưa xác định được hệ thống cần kiểm tra, hỏi rõ context trước khi thao tác. Kiểm tra dữ liệu live bằng tool, không suy trạng thái từ bộ nhớ.

Liên quan: [[memory/facts/ho-so-devops-va-he-thong]].

## Bổ sung tên context ngày 2026-10-07

Tên cũ `kpi-k8s-uat` tương ứng `kpi-uat`. `fsel-premium` là context khác chưa đi vào sử dụng theo người dùng; lần liệt kê 7 context ở trên là snapshot trước đó, không tự tăng số context live hoặc đổi kubeconfig. [[sources/readme/open-questions-answers-2026-10-07]]
