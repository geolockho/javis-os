---
name: "Lập kế hoạch chi phí và lịch trình chuyến xe"
description: "Tính quãng đường, chi phí thuê xe, nhiên liệu, phí đường bộ và lịch sạc cho chuyến đi."
group: "AI"
origin: javis-learned
status: active
created: 2026-10-29
---
## Khi nào dùng
- Khi người dùng cần ước tính chi phí cho chuyến đi bằng xe thuê hoặc xe cá nhân.
- Khi cần so sánh xe điện với xe xăng theo cùng một lịch trình.
- Khi cần lập lịch chạy xe, dừng nghỉ hoặc sạc xe điện theo từng chặng.
- Ví dụ: tính tổng chi phí hai ngày, kiểm tra xe điện có đủ pin đi một cung đường, hoặc tính lại lịch trình sau khi đổi xe.

## Chuẩn bị
- Lấy ngày, giờ xuất phát, giờ về và các điểm dừng từ người dùng.
- Xác định quãng đường từng chặng bằng nguồn bản đồ hoặc thông tin người dùng cung cấp.
- Ghi riêng số liệu đã xác minh, số người dùng cung cấp và giả định cần ước tính.
- Với xe thuê, xác nhận giá theo ngày, cách tính ngày thuê, km miễn phí và phí vượt km.
- Với xe xăng, lấy mức tiêu thụ và giá nhiên liệu phù hợp với xe, thời điểm và địa hình.
- Với xe điện, lấy dung lượng pin khả dụng, mức tiêu thụ, pin đầu hành trình và giới hạn sạc đã biết.
- Thu thập vị trí trạm sạc, công suất, thời gian sạc và cách thanh toán nếu có nguồn đáng tin cậy.
- Lấy phí cao tốc, cầu đường theo đúng loại xe và các trạm thực sự đi qua.
- Nếu thiếu dữ liệu, dùng khoảng ước tính có ghi rõ giả định; không trình bày như số liệu đã xác minh.

## Cách chạy
- Tổng quãng đường = tổng quãng đường các chặng xe chạy, cộng các đoạn vòng đã biết.
- Chi phí thuê = số ngày tính tiền nhân giá thuê mỗi ngày.
- Phí vượt km = max(0, tổng km - tổng km miễn phí) nhân đơn giá vượt km.
- Chi phí nhiên liệu = tổng km nhân mức tiêu thụ trên 100 km, chia 100, rồi nhân giá mỗi đơn vị nhiên liệu.
- Chi phí xe điện gồm tiền thuê, phí đường bộ, phí sạc hoặc gửi xe và các khoản phát sinh đã biết.
- Mức pin cuối chặng = mức pin đầu chặng trừ năng lượng tiêu thụ; cộng năng lượng sạc khi có dừng sạc.
- Năng lượng tiêu thụ chặng = quãng đường nhân mức tiêu thụ tương ứng với loại đường, chia 100.
- Tổng chi phí chuyến đi = tiền thuê + năng lượng + phí đường bộ + phí vượt km + chi phí phát sinh.
- Trình bày khoảng thấp-cao khi một hoặc nhiều đầu vào chỉ là ước tính.

## Quy trình
1. Tóm tắt lịch trình theo ngày và thứ tự các điểm dừng.
2. Tính quãng đường cho từng chặng riêng, không gộp các đoạn chưa xác minh.
3. Ghi tổng km và nêu rõ phần nào chưa tính, như đường vòng hoặc điểm đón thêm.
4. Tính tiền thuê theo cách tính ngày của bên cho thuê; nếu chưa biết, nêu giả định.
5. Tính chi phí năng lượng cho từng xe bằng dữ liệu phù hợp với xe và đường đi.
6. Tính km được miễn phí trong toàn bộ thời gian thuê và phần km có thể vượt.
7. Tính phí cầu đường theo tuyến thực tế, loại xe và trạm thu phí liên quan.
8. Với xe điện, chia tuyến thành các chặng giữa những điểm có thể sạc.
9. Ước tính mức pin đầu và cuối mỗi chặng; điều chỉnh mức tiêu thụ cho đường đèo hoặc cao tốc nếu có căn cứ.
10. Ước tính thời gian sạc theo dải pin cần nạp và dữ liệu sạc hiện có.
11. Chèn thời gian dừng sạc, nghỉ và đổi lái vào lịch trình; không tính thời gian lái xe như thời gian trôi qua duy nhất.
12. Kiểm tra xe có tới được trạm kế tiếp và điểm nghỉ với lượng pin dự phòng hợp lý.
13. Đánh dấu chặng có độ chắc chắn thấp và tính phương án dự phòng khi có thể.
14. So sánh tổng chi phí các lựa chọn trên cùng quãng đường và cùng lịch trình.
15. Nêu đánh đổi có ảnh hưởng thực tế, như thời gian dừng, phụ thuộc trạm sạc hoặc phí trả xe muộn.
16. Kết luận ngắn gọn theo tiêu chí người dùng ưu tiên, chẳng hạn chi phí, thời gian hoặc độ chủ động.
17. Nêu dữ liệu còn thiếu có thể làm thay đổi kết quả và cách người dùng xác nhận chúng.

## Bẫy
- Không coi ngày thuê là 24 giờ hay ngày lịch nếu bên cho thuê chưa xác nhận cách tính.
- Không đoán đơn giá vượt km rồi ghi thành giá thật; nếu cần, đưa thành kịch bản riêng.
- Không dùng giá nhiên liệu cũ cho chuyến đi trong tương lai mà không ghi ngày áp dụng.
- Không dùng mức tiêu thụ trên đường bằng cho toàn bộ cung đường có đèo dốc.
- Không lấy dung lượng pin danh định làm dung lượng sử dụng được nếu chưa xác minh.
- Không giả định xe sạc đều nhanh từ mức pin thấp đến 100%; kiểm tra thời gian theo từng dải pin.
- Không giả định trạm sạc còn cổng trống, đang hoạt động hoặc cho phép tài khoản thuê mở phiên.
- Không mặc định tài khoản ứng dụng của người thuê điều khiển được xe hoặc thanh toán được phiên sạc.
- Không bỏ quên đường vòng, quãng đường di chuyển tại điểm đến, phí gửi xe hoặc giờ trả xe.
- Không biến một ước tính của trợ lý thành dữ kiện đã được người dùng xác nhận.

## Kiểm chứng
- Cộng lại từng chặng để kiểm tra tổng quãng đường.
- Kiểm tra các chặng đã được tính đúng một lần và theo đúng thứ tự.
- Đối chiếu phép tính km miễn phí và km vượt với số ngày thuê.
- Kiểm tra đơn vị mức tiêu thụ, giá nhiên liệu và chi phí trước khi cộng tổng.
- Đối chiếu phí đường bộ với tuyến thực đi và loại xe.
- Với xe điện, lần theo mức pin qua từng chặng và từng lần sạc.
- Kiểm tra giờ đến bằng tổng thời gian lái, dừng sạc và nghỉ.
- Gắn nhãn số liệu thực tế, thông tin từ nguồn và giả định trong phần trả lời.
- Nếu một đầu vào chưa chắc chắn, đưa ra khoảng kết quả và nói rõ yếu tố tạo ra khoảng đó.
- Kết thúc bằng các bước người dùng cần xác nhận để thu hẹp sai số.
