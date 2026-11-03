---
type: decision
provenance: mixed
origin: javis-learned
created: 2026-10-23
updated: 2026-10-24
---
**Quyết định:** Vòng đời kubeconfig của công cụ kubeconfig-generator, đã đưa vào code bản đầu: (1) dev xin namespace, request chờ admin duyệt; (2) SA, RoleBinding và token chỉ tạo khi dev bấm tải link, thời hạn token tính từ lúc tải; (3) link tải dạng `/dl#<token>`, dùng một lần, có hạn 15 phút, chỉ mở được khi đăng nhập SSO đúng email người xin; (4) mỗi lần cấp một SA riêng tên `dev-<user>-<rand>` có label `managed-by`, revoke là xoá SA và RoleBinding theo label, không xoá SA của người khác. [[conversations/2026-10-23]]

**Đề xuất của Javis, người dùng chưa chốt rõ:** (a) request đã duyệt mà chưa tải trong 24 giờ thì hết hạn, Javis đã hỏi lại con số này và chưa có trả lời; (b) mỗi dev tối đa 5 request đang chờ; (c) cờ `ALLOW_SELF_APPROVE` mặc định tắt; (d) admin là tài khoản GitLab hophu@atlantic.edu.vn, so khớp chính xác (đây là email git của người dùng, nhưng việc đặt làm admin chưa được ghi rõ là đã duyệt). [[conversations/2026-10-23]]

**Vì sao:** Token TokenRequest là JWT không thu hồi được, nên muốn revoke thật phải xoá SA. Không lưu kubeconfig trên server nên dev phải tải đúng lúc duyệt. Link đặt sau `#` để token không vào access log của ingress. Các điểm (a) đến (d) là Javis đề xuất khi soi đặc tả, không phải quyết định của người dùng.

**Áp dụng:** Khi sửa luồng cấp token hoặc revoke trong kubeconfig-generator, giữ đúng nhóm (1) đến (4) như đã chốt. Với nhóm đề xuất (a) đến (d), coi là mặc định có thể đổi, và hỏi người dùng trước khi dựa vào như quyết định đã chốt. Không đổi sang thời hạn token tính từ lúc xin, không cấp token trước khi dev tải, và không xoá theo tên tiền tố chung. Xem thêm [[kien-truc-kubeconfig-generator-da-duyet]] và [[tien-do-kubeconfig-generator-sau-cach-b]].
