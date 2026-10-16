---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---

# Quy ước vận hành DevOps từ các câu hỏi đã trả lời

**Nguồn:** File người dùng gửi qua Telegram ngày 2026-10-07 lúc 09:51, yêu cầu cập nhật brain. Các xác nhận không thay kiểm tra live. [[sources/readme/open-questions-answers-2026-10-07]]

- Argo CD: app trên cluster cài Argo CD dùng project default; app remote nên ở project tên tương ứng cluster. [[sources/readme/open-questions-answers-2026-10-07]]
- ApplicationSet đọc values: dùng git.files. [[sources/readme/open-questions-answers-2026-10-07]]
- Tên cũ kpi-k8s-uat tương ứng kpi-uat; dùng kpi-uat khi trao đổi/thao tác, không tự đổi kubeconfig live. [[sources/readme/open-questions-answers-2026-10-07]]
- fsel-premium là context khác chưa đi vào sử dụng; không đồng nhất với fsel-pt-teacher hoặc tự thêm vào danh sách context active. [[sources/readme/open-questions-answers-2026-10-07]]
- Người dùng xác nhận CA trong Secret SA khớp API TLS endpoint FKE; vẫn cần kiểm tra credential/TLS thực tế khi chẩn đoán. [[sources/readme/open-questions-answers-2026-10-07]]
- Case Sentry ingest/Relay đã xử lý được, closed theo người dùng; không suy ra nguyên nhân cuối cùng hoặc cấu hình mới. Retention/config kiểm tra linh hoạt theo từng lần lỗi. [[sources/readme/open-questions-answers-2026-10-07]]
- Submariner hiện chưa triển khai; chỉ hỏi và kiểm chứng điều kiện triển khai khi người dùng cần, không tự hỏi lại hoặc tạo task định kỳ. [[sources/readme/open-questions-answers-2026-10-07]]

Liên quan: [[memory/facts/kubectl-context-va-quyen-kiem-tra]], [[wiki/_open-questions]].
