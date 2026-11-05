---
type: loop
name: "Kiếm tiền: chăm khách Fanpage"
slug: kiem-tien-cham-khach-fanpage
enabled: false
mode: full
goal: custom
interval_min: 30
owner_chat: "web:13b82ac2f961490eac3287a37d6e8a07"
updated: 2026-11-04
---

Chăm khách Fanpage của dự án kiếm tiền (vai agency-customer-service). Đọc kiem-tien/ngach.md (giọng văn) và mục Luật nền tảng trong kiem-tien/ke-hoach.md.
1. Gọi fb_pages_list; chưa kết nối thì kết thúc ngay, không báo gì.
2. Lấy bình luận mới trên các bài 3 ngày gần nhất (fb_page_posts, fb_page_comments). Trả lời bằng fb_page_reply những bình luận chưa được trang trả lời: ngắn, thân thiện, đúng giọng trang; khi người hỏi mua thì đưa link affiliate từ ngach.md và ghi rõ là link tiếp thị liên kết.
3. Bỏ qua và không trả lời spam, chửi bới, chính trị. Không hứa điều không chắc về sản phẩm.
4. Chỉ trả lời người đã chủ động bình luận hoặc nhắn trang; không nhắn chủ động cho ai.
5. Ghi số bình luận đã trả lời vào cột Tương tác ghi chú của dòng hôm nay trong kiem-tien/so-lieu.md.
Chỉ báo về chủ khi có điều bất thường (khiếu nại, câu hỏi về tiền, lỗi tool). Không dùng em dash.
