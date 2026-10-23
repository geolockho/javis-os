---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
**Quyết định:** User duyệt kiến trúc Javis đề xuất cho công cụ kubeconfig-generator (FastAPI + Jinja2, uvicorn 1 worker, oauth2-proxy sidecar với provider GitLab, psycopg 3 + SQL thuần, client kubernetes mỗi cluster một ApiClient, job dọn dẹp chạy mỗi 5 phút có advisory lock, pytest). User sửa một điểm: DB chỉ dùng PostgreSQL. [[conversations/2026-10-23]]
**Vì sao:** Đây là bản thiết kế đã qua bước soi của Javis và user đã đồng ý, nên có thể bắt đầu viết code.
**Áp dụng:** Viết code theo kiến trúc trên, không đổi sang DB khác. User sẽ tự khai báo công cụ trong ArgoCD sau. Namespace test do user cung cấp sau khi deploy lên cluster. Fact quyet-dinh-cong-cu-kubeconfig-generator ghi trạng thái 'dừng chờ duyệt kiến trúc', nay đã cũ ở điểm này nhưng vẫn đúng ở các điểm khác (push thẳng main, commit hophu, secret qua k8s).
