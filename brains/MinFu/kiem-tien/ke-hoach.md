---
type: project
name: Dự án kiếm tiền tự vận hành
status: active
created: 2026-11-04
updated: 2026-11-04
owner_chat: "web:13b82ac2f961490eac3287a37d6e8a07"
---
# Dự án kiếm tiền tự vận hành (Fanpage + affiliate)

File gốc của dự án. Mọi agent, loop và lịch của dự án đọc file này TRƯỚC khi làm.

## Mục tiêu và ràng buộc (chủ dự án chốt 2026-11-04)
- Mục tiêu: 5.000.000đ/tháng. Mốc chính 30 ngày (05/12/2026), mốc dừng cuối 90 ngày (02/02/2027): không khả thi thì dừng và báo.
- Vốn: 2.000.000đ. Thời gian chủ dự án: coi như 0, chủ CHỈ quyết các việc liên quan tới tiền.
- Nền tảng: Facebook Fanpage. Kiếm tiền bằng link tiếp thị liên kết (Shopee Affiliate hoặc ACCESSTRADE); sau đó có thể thêm sản phẩm số.
- Ranh giới: không vi phạm pháp luật hay điều khoản nền tảng; không dùng thông tin công ty hiện tại của chủ; không chi tiền khi chưa được duyệt.
- Mức tự chủ: Javis tự đăng bài, tự trả lời bình luận và tin nhắn người nhắn tới.

## Luật nền tảng (bắt buộc)
- Không spam: không nhắn tin chủ động hàng loạt cho người lạ, không tự comment link vào nhóm hay trang người khác.
- Không câu tương tác giả (kiểu "comment 1 để nhận"), không đánh giá sản phẩm giả, không bịa trải nghiệm đã dùng.
- Bài có link affiliate ghi rõ đó là link tiếp thị liên kết. Không hứa công dụng y tế, tài chính.
- Ảnh tạo bằng AI không giả làm ảnh thật của khách hay sản phẩm đã dùng.
- Tối đa 3 bài/ngày. Không đăng lại nội dung có bản quyền của người khác.

## Quyết định tiền (chỉ chủ duyệt)
Khi cần chi (quảng cáo, công cụ, mua tên miền...): ghi 1 mục vào `kiem-tien/de-xuat-chi-tien.md` (số tiền, lý do, kỳ vọng, cách đo, hạn chót) rồi báo về khung chat chủ kèm nút Duyệt/Từ chối. Chưa có chữ "duyệt" của chủ thì KHÔNG chi.

## Lộ trình
| Giai đoạn | Ngày | Việc | Xong khi |
|---|---|---|---|
| 0. Nghiên cứu | 1-3 | Chọn ngách, chân dung người đọc, 20 sản phẩm affiliate đầu tiên, tên trang, giọng văn | `kiem-tien/ngach.md` có ngách đã chốt |
| 1. Dựng trang | 3-7 | Ảnh đại diện, ảnh bìa, giới thiệu, 10 bài nền (chưa link) | Fanpage kết nối và có 10 bài |
| 2. Chạy phễu | 7-30 | 2 bài/ngày (70% giá trị, 30% có link), trả lời khách, thử nghiệm A/B góc viết | Có click và đơn đầu tiên |
| 3. Nhân bản | 31-90 | Nhân bản dạng bài ra đơn, cân nhắc sản phẩm số, xin chi ads nếu số liệu cho phép | Đạt 5tr/tháng hoặc dừng |

Luật dừng: hết ngày 14 mà chưa có click affiliate thì đổi ngách. Hết ngày 45 doanh thu dưới 500.000đ thì đề xuất đổi mô hình. Ngày 90 chưa đạt thì dừng.

## Chỉ số đo (ghi vào `kiem-tien/so-lieu.md`)
- Tiến độ: giai đoạn hiện tại, việc đã xong so với lộ trình.
- Phễu: lượt tiếp cận, tương tác, click link, đơn, hoa hồng; tỷ lệ chuyển đổi từng bước.
- Chi phí: tiền đã chi; số lượt Javis chạy mỗi ngày (thay cho token khi chưa đo được token).

## Điều kiện bên ngoài (chủ phải làm một lần, Javis không làm thay được)
- [ ] Bật "AI tự vận hành" (chủ báo đã bật 2026-11-04)
- [ ] Tạo Fanpage và kết nối ở trang Kết nối, thẻ "Facebook Messenger"
- [ ] Đăng ký Shopee Affiliate hoặc ACCESSTRADE (cần CCCD, tài khoản ngân hàng), gửi Javis mã hoặc link
- [ ] (Khi cần ads) kết nối Meta Ads

## Hệ thống vận hành
- Agent điều phối: `agents/kt-giam-doc.md`. Nhóm chat: "Dự án kiếm tiền".
- Kiến thức tích luỹ: `kiem-tien/playbook.md`. Nháp bài: `kiem-tien/nhap/`. Báo cáo: `kiem-tien/bao-cao/`.
