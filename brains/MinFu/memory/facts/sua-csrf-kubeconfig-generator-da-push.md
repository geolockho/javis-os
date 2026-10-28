---
type: business
provenance: source
origin: javis-learned
created: 2026-10-28
updated: 2026-10-28
---
Ngày 2026-10-28 user yêu cầu copy thay đổi sáng sang D:\FSEL\other-services\kubeconfig-generator và push. Javis đã push lên origin/main, nhánh từ 5201191 lên facc6f9 ([[conversations/2026-10-28]]).

- **659168b**: sửa lỗi `{"detail":"Sai nguồn gửi (CSRF)"}`. Đổi Referrer-Policy sang `same-origin`. Khi Origin là `null` thì kiểm Sec-Fetch-Site, chỉ chấp nhận `same-origin` hoặc `none`. Có 2 test mới trong tests/test_flow.py.
- **facc6f9**: README đổi các lệnh gán label namespace thật (fsel-prod, 5sis-testing-n...) sang team-a. Tách riêng để revert nếu user muốn giữ tên thật. Việc này trả lời câu hỏi còn treo trong [[kubeconfig-generator-da-push-va-deploy-fsel-local]].

Nguyên nhân CSRF là suy luận từ hành vi Chrome, chưa thấy header Origin thật (cần xác minh). Test chưa chạy vì thiếu pytest, fastapi và TEST_DATABASE_URL (thực tế tính đến 2026-10-28). Pod trên fsel-local vẫn là image cũ cho đến khi build và rollout (thực tế tính đến 2026-10-28).
