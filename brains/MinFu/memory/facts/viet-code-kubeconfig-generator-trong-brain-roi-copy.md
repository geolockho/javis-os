---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-23
updated: 2026-10-23
---
Ngày 2026-10-23 người dùng hỏi có thể viết code trong brain rồi copy sang `D:\FSEL\other-services\kubeconfig-generator` không, và cách nào tốn token hơn. Javis đề xuất viết trong brain, người dùng trả lời "oke viết đi".

**Vì sao:** công cụ ghi và sửa file của Javis từ chối thư mục nằm ngoài brain. `javis_edit_file` chỉ gửi đoạn cần sửa, nên tốn ít token hơn việc ghi đè cả file bằng PowerShell. Lệnh copy không đưa nội dung qua model.

**Áp dụng:**
- Bản gốc nằm tại `workspace/kubeconfig-generator` trong brain MinFu. Repo ở `D:\FSEL\...` là bản copy, không sửa tay ở đó vì lần copy sau sẽ ghi đè.
- Copy bằng `robocopy /E`, loại trừ `.git`, `.env`, `.venv`, `__pycache__`, không dùng `/MIR`.
- Commit và push chạy trong repo thật, dưới tên hophu, đẩy thẳng main.
- `.env` chỉ có ở repo thật, trong brain chỉ có `.env.example`.
- Việc copy bằng robocopy chưa được kiểm chứng (thực tế tính đến 2026-10-23).
