---
type: preference
provenance: user
origin: javis-learned
created: 2026-10-07
updated: 2026-10-07
---

# Hiển thị thống kê token cuối mỗi câu trả lời

**Yêu cầu:** Từ ngày 2026-10-07, người dùng muốn cuối mỗi câu trả lời có thống kê token của lượt trả lời, chu kỳ 5 giờ và tuần.

## Các thông tin cần hiển thị

1. Số token đã sử dụng cho câu trả lời hiện tại và phần trăm so với tổng token trong chu kỳ 5 giờ.
2. Số token còn lại trong chu kỳ 5 giờ.
3. Số token còn lại trong tuần.

**Cách áp dụng:** Dùng số liệu thực tế từ gateway/provider hoặc evidence phù hợp, ghi rõ phạm vi đếm và mẫu số của tỷ lệ khi có dữ liệu. Không lấy token lượt trước thay lượt hiện tại, không lấy ngân sách goal của agent thay hạn mức tài khoản, không coi tổng token đo trên máy là quota còn lại. Nếu không có usage của lượt hiện tại hoặc hạn mức/reset 5 giờ/tuần, vẫn giữ các mục người dùng yêu cầu và ghi "chưa có dữ liệu" cho phần thiếu; không bịa hoặc ước đoán thành số thật.

**Giới hạn:** Khi usage đầy đủ chỉ được runtime ghi sau khi câu trả lời kết thúc, assistant chưa thể biết chính xác token toàn lượt trong lúc soạn câu trả lời. Muốn số chính xác cần gateway/provider cung cấp hoặc bổ sung sau khi hoàn tất; việc lưu sở thích này không có nghĩa đã chỉnh cơ chế gateway.

## Cập nhật theo yêu cầu ngày 2026-10-07 lúc 13:47

Người dùng yêu cầu kiểm tra vì sao ba mục trên đều ghi "chưa có dữ liệu" và đổi sang các thông số thực sự có dữ liệu. Quy ước mới thay thế định dạng cuối câu trả lời cũ:

1. Token và số lượt đã dùng trong cửa sổ trượt 5 giờ, theo gateway `/usage/tong-quan` và trường `cua_so`.
2. Token đã dùng hôm nay, theo gateway `/usage/summary?period=today` và trường `kpi.tokens`.
3. Token đã dùng trong tuần này, theo gateway `/usage/summary?period=this_week` và trường `kpi.tokens`.

Các số này là **mức đã dùng**, không phải quota còn lại của tài khoản. `tran_khai = 0` ở lần kiểm tra 13:47 nghĩa là chưa khai trần 5 giờ; `moc_so_sanh` chỉ là đỉnh dùng từng ghi nhận, không phải hạn mức nhà cung cấp. Token của câu trả lời hiện tại chưa có trước khi runtime hoàn tất lượt nên không đưa số lượt hiện tại vào footer. Mỗi câu trả lời chỉ hiển thị số lấy từ gateway ở lượt đó; nếu gateway lỗi thì ghi rõ lỗi hoặc bỏ footer thay vì dùng số cũ.

**Bằng chứng lúc cập nhật:** Gateway local trả `/usage` thành công; `/usage/tong-quan?period=today&refresh=0` có `cua_so.tokens = 10146605`, `cua_so.turns = 108`, `tran_khai = 0`; `/usage/summary?period=today&refresh=0` có `kpi.tokens = 10304192`; `/usage/summary?period=this_week&refresh=0` có `kpi.tokens = 53752871`. Các số này chỉ là snapshot lúc kiểm tra, không dùng lại để báo cáo tương lai.

**Nguồn cập nhật:** Tin nhắn người dùng qua Telegram ngày 2026-10-07 lúc 13:47: "check xem tại sao lại không có dữ liệu, đổi sang thống kê thông số mà có dữ liệu".

## Cập nhật theo yêu cầu ngày 2026-10-07 lúc 16:10

Người dùng gửi ảnh Codex Usage remaining với hai tỷ lệ `5h` và `Weekly`, yêu cầu **hiển thị phần trăm hạn mức còn lại thay các con số token cụ thể**. Quy ước này thay thế footer mức dùng lúc 13:47:

- Cuối mỗi câu trả lời, nếu lấy được dữ liệu live, ghi ngắn: `Codex còn: 5 giờ X%; tuần Y%.` Có thể kèm giờ reset Việt Nam khi hữu ích.
- Lấy dữ liệu bằng lệnh đọc `python Javis/codex-usage-percent.py` trong brain MinFu; helper hỏi `account/rateLimits/read` từ Codex app-server local. `primary` phải là 300 phút, `secondary` phải là 10080 phút; `remaining = 100 - usedPercent`.
- Đây là **phần trăm hạn mức Codex còn lại**, không phải phần trăm token. Không suy tỷ lệ này từ `/usage` của Javis, vì gateway đó chỉ đếm token đã dùng và không có mẫu số hạn mức tài khoản.
- Nếu truy vấn live lỗi, nói ngắn rằng không lấy được hạn mức, kèm lỗi thật; không dùng số cũ từ ảnh hoặc log làm số hiện tại.

**Bằng chứng lúc cập nhật:** Ảnh Telegram `inbox/telegram/photo_182.jpg` cho thấy `5h 34%`, `Weekly 90%` tại lúc người dùng gửi; lần đọc live sau đó từ Codex app-server trả `primary.usedPercent=76` và `secondary.usedPercent=12`, tương đương 24% và 88% còn lại. Các số này chỉ là snapshot, không dùng lại về sau.

**Nguồn cập nhật:** Tin nhắn người dùng qua Telegram lúc 16:10 ngày 2026-10-07: "đổi thống kê token theo % như này, thay vì để con số cụ thể".

## Nguồn

Tin nhắn trực tiếp của người dùng qua Telegram, chat_id `1110969232`, ngày 2026-10-07 lúc 09:58 (Asia/Ho_Chi_Minh):

> lưu vào bộ nhớ: sau này sẽ kèm các thông tin sau ở cuối mỗi câu trả lời:
> 1. số token đã sử dụng cho câu trả lời này, chiếm bao nhiêu % tổng token trong chu kỳ 5h
> 2. số token còn lại trong chu kỳ 5h
> 3. số token còn lại trong tuần
