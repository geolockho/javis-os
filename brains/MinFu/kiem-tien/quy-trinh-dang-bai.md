---
type: guide
status: active
version: v1
created: 2026-11-05
updated: 2026-11-05
---
# Quy trình đăng bài Fanpage Nhà Nhỏ Sống Gọn

Lịch "Kiếm tiền: đăng bài Fanpage" (11:30 và 20:30) làm ĐÚNG file này. Quy trình nằm ở file thay vì trong lời nhắc của lịch, vì lời nhắc lịch bị cắt ở 2.000 ký tự.

Đọc trước: `kiem-tien/ke-hoach.md` (mục Luật nền tảng là bắt buộc), `kiem-tien/ngach.md`, `kiem-tien/playbook.md`, `kiem-tien/giong-van.md` (BẮT BUỘC, đặc biệt mục "Dạng ngắn").

## 1. Điều kiện

1. Chưa có `kiem-tien/ngach.md`: dừng, không báo gì.
2. Gọi `fb_pages_list`. Chưa kết nối Fanpage: chỉ đảm bảo `kiem-tien/nhap/` có ít nhất 4 nháp, rồi kết thúc, không báo chủ.

## 2. Chọn loại bài

Có hai loại, cả hai đều viết theo **Dạng ngắn** trong `giong-van.md`:

- **Bài sản phẩm:** một món đồ, ảnh lấy từ chính trang sản phẩm, link affiliate để dưới comment.
- **Bài mẹo ngắn:** một mẹo hoặc một quan sát đời ở trọ, ảnh thật giấy phép tự do, không link.

Cách chọn:

- **Chưa có công cụ tìm sản phẩm Shopee** (chưa có plugin `shopee_affiliate`, tức chưa có Open API): chỉ đăng bài mẹo ngắn. Không đăng bài sản phẩm chỉ có ảnh mà không có link.
- **Đã có công cụ tìm sản phẩm:** lượt 11:30 đăng bài sản phẩm, lượt 20:30 đăng bài mẹo ngắn. Chủ có thể đổi tỷ lệ này.

## 3. Bài mẹo ngắn

1. Chọn nháp theo THỨ TỰ CỐ ĐỊNH: `bai-gioi-thieu.md` (nếu còn), rồi `bai-02.md`, `bai-03.md`... theo số tăng dần; bỏ qua thư mục `_v1`. Hết nháp thì viết mới theo `ngach.md` và `playbook.md`.
2. Nháp chưa có `giong_van: v4` trong frontmatter: rút gọn theo Dạng ngắn. Chọn MỘT ý đắt nhất của nháp, viết 1-3 câu (tối đa khoảng 45 từ), có một chút cảm xúc hoặc tự trào, kết bằng một câu hỏi ngắn nếu hợp. Phần còn lại của nháp cũ giữ lại dưới tiêu đề `## Ý còn lại` để lần sau tách thành bài khác. Ghi đè nháp kèm `giong_van: v4`.
3. Không bịa trải nghiệm cá nhân, không bịa số liệu.
4. Ảnh: theo mục 5.

## 4. Bài sản phẩm (chỉ khi đã có công cụ tìm sản phẩm)

1. Chọn từ khoá theo danh sách 20 từ khoá trong `ngach.md`, xoay vòng, không lặp món đã đăng trong 7 ngày (xem `kiem-tien/da-dang/`).
2. Tìm sản phẩm qua công cụ Shopee. Ưu tiên món bán chạy, đánh giá tốt, giá phù hợp người ở trọ. Lấy link affiliate, tên món, giá, ảnh sản phẩm.
3. **Ảnh:** tải ảnh từ trang sản phẩm vào `attachments/fb/`, kiểm bằng `javis_describe_image`: KHÔNG watermark, không logo shop, không chữ hay giá in đè lên ảnh. Ảnh chính trượt thì thử các ảnh khác trong bộ ảnh của chính sản phẩm đó. Cả bộ đều trượt thì đổi sang sản phẩm khác. Ảnh sản phẩm chỉ dùng cho bài nói về đúng sản phẩm đó.
4. **Thân bài:** 1-3 câu theo Dạng ngắn, nói về công dụng hoặc cái hay của món đồ dựa trên mô tả sản phẩm. KHÔNG viết như đã dùng ("t dùng rồi", "pin cả tháng"). Không chèn link trong thân bài. Dòng cuối: "Link ở cmt nha 👇".
5. Đăng bằng `fb_page_photo`, rồi ngay sau đó comment vào chính bài đó bằng `fb_page_reply` với `post_id` của bài vừa đăng: link món chính, có thể thêm tối đa 4 link món liên quan đúng chủ đề, mỗi link một dòng kèm tên món, dòng cuối "(link tiếp thị liên kết)". Không đủ món khớp thì comment ít link hơn, không độn.
6. Lưu hồ sơ bài vào `kiem-tien/da-dang/sp-YYYYMMDD-HHMM.md` (frontmatter: loai: san-pham, tu_khoa, ten_mon, link, anh, post_id, comment_id).

## 5. Ảnh cho bài mẹo ngắn

Ảnh thật, KHÔNG dùng ảnh AI (không gọi `javis_generate_image`). Tìm qua Openverse:
`curl "https://api.openverse.org/v1/images/?q=<từ khoá tiếng Anh>&license=cc0,pdm&page_size=20"`.
Chỉ dùng license cc0 hoặc pdm. Tải ảnh ứng viên vào `attachments/fb/`, kiểm bằng `javis_describe_image`: không watermark, không logo, không chữ chèn lên ảnh, không mặt người nhận ra được, khớp chủ đề bài. Trượt thì thử ảnh khác, đổi từ khoá tối đa 3 lần. Vẫn không có thì đăng bài chữ bằng `fb_page_post`.

## 6. Đăng và lưu

1. Bài mẹo: có ảnh thì `fb_page_photo`, không có thì `fb_page_post`.
2. Chuyển nháp sang `kiem-tien/da-dang/` kèm `status: posted`, `posted_at`, `post_id`, `anh`, `anh_nguon`.
3. Đăng lỗi: ghi lỗi vào `kiem-tien/so-lieu.md` và báo chủ một dòng nêu đúng lỗi. Đăng thành công: báo một dòng tên bài, loại bài, có link hay không.

## Luật giữ nguyên

- Tối đa 3 bài/ngày. Không comment vào trang hay nhóm của người khác.
- Có link thì ghi rõ là link tiếp thị liên kết.
- Không bịa trải nghiệm, không đánh giá giả, không hứa công dụng y tế hay tài chính.
