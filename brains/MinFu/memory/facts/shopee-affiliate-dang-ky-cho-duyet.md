---
type: business
provenance: user
origin: javis-learned
created: 2026-11-05
updated: 2026-11-05
source: chat 2026-11-05 (13b82ac2)
---
Người dùng đã đăng ký Shopee Affiliate và đang chờ duyệt (thực tế tính đến 2026-11-05). Fanpage là kênh thử nghiệm affiliate đã chọn; kế hoạch thử tối đa 90 ngày được ghi trong [[ke-hoach-thu-nghiep-affiliate-fanpage]].

## Việc comment link affiliate: tạm hoãn (quyết định 2026-11-05)

Người dùng muốn thêm việc comment link affiliate vào các bài trên Fanpage Nhà Nhỏ Sống Gọn, khoảng 5 link mỗi bài. Ngày 2026-11-05 người dùng quyết định **tạm hoãn** việc này cho tới khi họ gửi App ID của Shopee Affiliate Open API. Sau khi có App ID, Javis tự tìm sản phẩm, tự tạo link và bắt đầu chu trình comment.

**Vì sao:** lúc đó chỉ có 1 link dùng được (danh mục Thiết bị gia dụng), chưa có link sản phẩm cụ thể. Comment lặp một link vào mọi bài dễ bị coi là spam.

**Áp dụng:** khi người dùng gửi App ID: (1) dựng plugin `shopee_affiliate` (tìm sản phẩm theo từ khóa, tạo link), để `enabled: false` cho người dùng tự bật; App Secret nhập ở chỗ riêng, không dán vào chat. (2) KHÔNG tạo lịch comment riêng nữa (đổi ngày 2026-11-05): lịch đăng bài tự comment link ngay sau khi đăng bài sản phẩm, theo `kiem-tien/quy-trinh-dang-bai.md`. Mỗi bài sản phẩm 1 comment, tối đa 5 link đúng món, kèm "(link tiếp thị liên kết)"; chỉ comment trên trang của mình. Khi có công cụ, lượt 11:30 là bài sản phẩm, 20:30 là bài mẹo ngắn.
