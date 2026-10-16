---
type: decision
provenance: user
origin: javis-learned
created: 2026-10-08
updated: 2026-10-14
---
Ngày 2026-10-08, người dùng yêu cầu chuyển model cho việc nền (tự học, loop, nhắc việc) sang Haiku để giảm chi phí, còn chat chính giữ Sonnet hoặc Opus. Javis báo đã đổi và server xác nhận cấu hình việc nền là Haiku qua provider Claude CLI (thực tế tính đến 2026-10-08) [[conversations/2026-10-08]].

Cũng trong hội thoại ngày 2026-10-08: Javis lưu ý Javis đang đăng nhập bằng gói subscription nên việc nền Haiku KHÔNG trừ vào tín dụng khuyến mãi $25 của Console; tín dụng đó chỉ giảm khi Javis gọi bằng API key, mà máy chưa nhập key [[tin-dung-khuyen-mai-anthropic]] [[conversations/2026-10-08]].

**Vì sao:** kéo dài hạn mức và số dư khi việc nền chạy lặp lại.
**Áp dụng:** khi cần đổi model nền, giữ Haiku làm mặc định; không đổi model chat chính trừ khi người dùng yêu cầu.
