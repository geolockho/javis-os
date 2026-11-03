# Javis Index (tầng vận hành)

> Tự sinh từ file - ĐỪNG sửa tay. Chỉ mục mọi năng lực của Javis trong brain này để bất kỳ AI/engine đọc 1 chỗ là hiểu Javis làm được gì. Song song `wiki/index.md` (tri thức).

**Tổng quan:** 0 agents · 6 skills · 0 workflows (0 bật) · 0 loops (0 bật) · 28 plugins (27 chạy)

## Agents
_(chưa có)_

## Skills
### AI
- **Ingest Source** (`ingest-source`) - Tiêu hoá một source thô vào Second Brain, chưng cất thành tri thức wiki tích luỹ.
- **Javis Builder** (`javis-builder`) - Tạo hoặc sửa năng lực của Javis: agent, skill, workflow, loop, plugin. Kèm mẫu file chuẩn và luật chống trùng.
- **Lint Wiki** (`lint-wiki`) - Rà soát sức khoẻ wiki của Second Brain, trả về danh sách vấn đề. Không tự sửa hàng loạt.
- **Notes** (`notes`) - Lưu tin nhắn hiện tại nguyên văn vào sources/ (kèm ảnh), tự chưng cất lên wiki nếu note đáng.
- **Query Wiki** (`query-wiki`) - Khai thác tri thức trong Second Brain: tổng hợp, so sánh, giả thuyết. Trả lời có trích dẫn.
### Marketing
- **HTML sang Webcake** (`html-to-webcake`) - Chuyển trang HTML thành file .pke mở được trong trình dựng Webcake, giữ đúng màu, cỡ chữ, ảnh và bố cục của bản gốc.

## Workflows
_(chưa có)_

## Loops
_(chưa có)_

## Plugins (tool/hook native cho mọi engine)
- **Thời gian & ngày** (`datetime-vn`) - bundled/chạy · tools: javis_now, javis_date_add · Xem ngày giờ hiện tại theo múi giờ chọn ở Cài đặt và tính ngày tương đối (mai, mốt, N ngày nữa, tuần trước). Thuần stdlib, chỉ đọc, không cần mạng.
- **Điều khiển app trên máy** (`desktop-apps`) - bundled/chạy · tools: javis_app_list, javis_app_open, javis_app_close · Mở, đóng và liệt kê ứng dụng trên CHÍNH MÁY đang chạy Javis (Windows, macOS, Linux có màn hình) theo lời người dùng, ví dụ "mở Chrome", "tắt Excel", "đang mở app nào". Tự chặn và nói rõ khi Javis chạy trong Docker trên máy chủ, vì khi đó máy chạy Javis không phải máy của người dùng.
- **Theo dõi Facebook (Apify)** (`fb-monitor-apify`) - bundled/chạy · tools: fb_monitor · Theo dõi Trang/Nhóm CÔNG KHAI Facebook tìm bài nhiều share qua dịch vụ Apify. Chỉ đọc, không đụng tài khoản cá nhân, chạy tốt trên VPS. Dùng token của kết nối "facebook-monitor".
- **Tạo và xem ảnh (ChatGPT)** (`image-chatgpt`) - bundled/chạy · tools: javis_generate_image, javis_describe_image · Tạo ảnh từ mô tả bằng GÓI ChatGPT đang đăng nhập (OAuth) - không cần OpenAI API key. Dùng Codex Responses API + tool image_generation (gpt-image-2). Ảnh lưu vào attachments/ của vault để nhúng thẳng vào chat. Kèm tool XEM ảnh, để ChatGPT nhìn ảnh trong brain rồi tả lại bằng chữ, để cả engine không tự xem được ảnh (OpenRouter, Gemini API...) cũng biết trong ảnh có gì. Cần đã kết nối ChatGPT ở trang Model.
- **Đấu thêm MCP** (`javis-connect`) - bundled/chạy · tools: javis_add_mcp · Đấu một MCP server vào kho Kết nối của Javis ngay từ chat, để nó HIỆN ra trang Kết nối như mọi tài khoản khác. Trước tool này Javis chỉ còn đường `claude mcp add` - thứ rơi vào config riêng của Claude Code, không bộ não nào khác thấy và người dùng cũng không thấy trên trang Kết nối.
- **GitHub trong khung chat** (`javis-github`) - bundled/chạy · tools: javis_github · Xem trạng thái repo GitHub của khung chat (nhánh, PR, CI, merge) và xếp việc kế tiếp để Javis tự làm khi PR hiện tại đã merge xong.
- **Việc chạy nền** (`javis-job`) - bundled/chạy · tools: javis_job · Theo dõi lệnh chạy ngầm engine bỏ lại (render, build, tải về). Dặn trước "xong thì làm tiếp gì", xem việc đang chạy, dừng một việc. Xong là Javis tự báo về đúng khung chat và tự làm tiếp.
- **Cookies** (`javis-login`) - bundled/chạy · tools: javis_login · Mở trang web cần đăng nhập bằng phiên đăng nhập chủ đã cất ở trang Cookies. Chỉ trả nội dung trang, không bao giờ trả cookie.
- **Trí nhớ qua chat** (`javis-memory`) - bundled/chạy · tools: javis_memory · Cho Javis xem, sửa, quên ghi nhớ của brain, bật tắt việc lưu ghi nhớ mới, sửa hồ sơ chung và thu hồi bài học của trợ lý khi người dùng nhắn. Thay cho các danh sách trí nhớ và bài học từng nằm ở cột Cài đặt. Chỉ phiên của chủ thấy tool này.
- **Việc của tôi và thói quen** (`javis-mine`) - bundled/chạy · tools: javis_mytask · Thêm việc vào tab Của tôi trên trang Nhiệm vụ, xem việc hôm nay và thói quen, và tích xong một việc hoặc một buổi thói quen khi người dùng báo đã làm xong, ngay từ chat.
- **Chỉ huy thông báo** (`javis-notify`) - bundled/chạy · tools: javis_notify · Xem và đổi thông báo nào được báo. Mỗi nhóm thông báo có một chế độ (tất cả, đáng chú ý trở lên, chỉ tin khẩn, tắt); lọc hoặc luôn báo một loại tin; hoàn tác thay đổi của Javis Core.
- **Tạo plugin qua chat** (`javis-plugin`) - bundled/chạy · tools: javis_plugin · Cho Javis tạo, đọc và sửa plugin của người dùng ngay tại chỗ khi được nhờ trong chat, không phải tải file zip về rồi tải lên lại. Plugin mới hoặc vừa đổi mã luôn nằm TẮT, chủ đọc mã rồi tự bật ở trang Plugins. Chỉ phiên của chủ thấy tool này.
- **Bộ phán xử của bot nhóm** (`javis-reply-policy`) - bundled/chạy · tools: javis_reply_policy, javis_reply_policy_tune · Cho Javis đọc số liệu bộ phán xử (bot nói hay im trong nhóm, vì sao, bị chấm sai ở đâu) và chỉnh nó khi chủ nhờ, rồi hoàn lại được. Chỉ phiên của chủ thấy hai tool này, bot chăm khách không bao giờ thấy.
- **Đặt việc định kỳ & nhắc hẹn** (`javis-schedule`) - bundled/chạy · tools: javis_schedule · Tạo/liệt kê/huỷ việc chạy định kỳ và nhắc hẹn ngay từ chat. Tự chọn kho - việc lặp và bền thì ghi Javis/loops/<slug>.md để sửa được trong Obsidian; nhắc một lần hoặc lịch cron thì vào kho nhắc hẹn (đã có sẵn cron 5 trường). Thay cho việc gõ YAML tay hoặc curl.
- **Giao việc Kanban** (`javis-task`) - bundled/chạy · tools: javis_task · Giao một việc nền vào hàng đợi Kanban và xem việc đang chạy tới đâu, ngay từ chat. Trước tool này chỉ engine chạy được lệnh máy (Claude Code, Codex) mới giao việc được, vì đường duy nhất là curl POST /kanban/task - năm engine API đứng ngoài.
- **Quản lý nhóm chat** (`javis-team`) - bundled/chạy · tools: javis_team · Tạo, sửa, lưu trữ và xoá nhóm chat, thêm bớt trợ lý, chọn trưởng nhóm, tạo trợ lý mới với model riêng rồi ghép vào nhóm, ngay từ chat và trên mọi engine. Trước tool này phải vào trang Nhóm bấm tay, hoặc điều khiển trình duyệt.
- **Điều khiển dashboard** (`javis-ui`) - bundled/chạy · tools: javis_ui · Mở trang, mở file trong brain, mở một việc Kanban hoặc cuộn khung chat trên dashboard đang mở, theo lời người dùng nói hoặc gõ. Dashboard xác nhận đã làm xong ngay trong lượt; không có tab nào mở thì tool nói rõ.
- **Theo dõi trang web** (`javis-watch`) - bundled/chạy · tools: javis_watch · Canh một trang web theo lịch mà không tốn token - báo khi trang đổi, khi xuất hiện một cụm chữ hoặc khi có giá dưới ngưỡng (hiểu 1.250.000đ, 1,5 triệu, 250k, $20). Chỉ gọi AI khi bật tóm tắt.
- **Lịch sử quy trình** (`javis-workflow`) - bundled/chạy · tools: javis_workflow · Xem các lần chạy quy trình gần đây và kết quả từng lần, ngay từ chat. Trước tool này, chạy quy trình xong là kết quả mất, hỏi "quy trình chạy gần nhất ra sao" Javis không có gì để tra.
- **Kiểm tra Messenger** (`messenger-health`) - bundled/chạy · tools: messenger_check, messenger_repair · Rà kết nối bot Messenger của từng Fanpage (token Trang, quyền, webhook, Trang gắn app, bot đang trực) và sửa tự động phần webhook khi bot im lặng.
- **Meta Ads (Graph API)** (`meta-ads-graph`) - bundled/chạy · tools: meta_ads_accounts, meta_ads_insights, meta_ads_campaigns, meta_ads_get · Đọc số liệu quảng cáo Facebook/Instagram (tài khoản ads, chiến dịch, hiệu suất) qua Graph API, dùng token của kết nối "Meta Ads (tự tạo app)". CHỈ ĐỌC, không tiêu tiền.
- **Facebook Trang (Graph API)** (`meta-pages-graph`) - bundled/chạy · tools: fb_pages_list, fb_page_posts, fb_page_comments, fb_page_post, fb_page_photo, fb_page_album, fb_page_video, fb_page_edit, fb_page_delete, fb_page_reply · Quản lý Trang/Fanpage Facebook qua Graph API - liệt kê Trang, đọc bài và bình luận (chỉ đọc), đăng bài/ảnh/video/album, sửa chữ, xoá bài và trả lời bình luận (toàn quyền). Dùng Fanpage đã nối ở thẻ Facebook Messenger (trang Kết nối), hoặc kết nối "Facebook Trang" trong Kho nếu có.
- **Nhật ký dùng tool** (`tool-audit`) - bundled/tắt · tools: javis_tool_stats · hooks: post_tool_call · Đếm số lần MỖI tool được engine gọi (qua hook post_tool_call) và cho xem thống kê tool hay dùng. Đây là ví dụ minh hoạ cơ chế HOOK của plugin. Mặc định TẮT - bật qua POST /plugins/toggle (slug=tool-audit) để thử.
- **Tin thoại** (`voice-note`) - bundled/chạy · tools: javis_voice_note · Javis ghi một đoạn nói ngắn (tối đa 1000 ký tự) thành file mp3 trong attachments/voice/ rồi nhúng vào câu trả lời. Khung chat hiện trình phát, Telegram nhận file âm thanh. Dùng giọng Edge miễn phí theo ngôn ngữ của câu.
- **Đọc video YouTube** (`youtube-read`) - bundled/chạy · tools: javis_youtube_read · Đọc lời thoại (phụ đề) của video YouTube từ link để tóm tắt. Tự đổi qua 6 kiểu trình phát rồi tới yt-dlp khi YouTube chặn máy chủ. Không cần đăng nhập, không cần API key.
- **Zalo nhóm - tag người, ghi chú, nhắc hẹn, poll** (`zalo-group`) - pack/chạy · tools: zalo_group_members, zalo_send_mention, zalo_create_note, zalo_create_reminder, zalo_create_poll · Tag ĐÚNG người trong nhóm Zalo (nói tên, Javis tự tìm ID Zalo thật), liệt kê thành viên, tạo ghi chú nhóm, tạo nhắc hẹn và tạo poll, bằng chính tài khoản đã quét QR ở trang Kết nối. Bù đúng chỗ MCP chuẩn của zalo-agent-cli còn thiếu - nó chỉ có bảy tool và tool gửi tin chỉ nhận chữ.
- **Gửi ảnh & file qua Zalo** (`zalo-image`) - pack/chạy · tools: zalo_send_image · Gửi ẢNH hoặc FILE qua Zalo kèm lời nhắn, bằng chính tài khoản đã quét QR ở trang Kết nối. Bù đúng chỗ MCP chuẩn của zalo-agent-cli còn thiếu - tool zalo_send_message của nó chỉ nhận chữ.
- **Đọc ảnh trong nhóm Zalo** (`zalo-read-images`) - pack/chạy · tools: zalo_read_images · Lấy ẢNH người ta gửi trong nhóm Zalo về brain (attachments/zalo/) rồi cho bộ não xem được nội dung ảnh, bằng chính tài khoản đã quét QR ở trang Kết nối. Engine tự xem được ảnh (Claude Code, Codex) mở thẳng file; engine khác nhận lời tả của ChatGPT trên gói đang đăng nhập. Bù đúng chỗ MCP chuẩn của zalo-agent-cli còn thiếu - nó chỉ trả link ảnh và giữ tin 2 giờ.
