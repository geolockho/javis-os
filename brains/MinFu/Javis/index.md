# Javis Index (tầng vận hành)

> Tự sinh từ file - ĐỪNG sửa tay. Chỉ mục mọi năng lực của Javis trong brain này để bất kỳ AI/engine đọc 1 chỗ là hiểu Javis làm được gì. Song song `wiki/index.md` (tri thức).

**Tổng quan:** 25 agents · 55 skills · 1 workflows (0 bật) · 1 loops (1 bật) · 28 plugins (27 chạy)

## Agents
- **Kiến trúc sư phần mềm** (`ecc-architect`) - Thiết kế hệ thống, cân nhắc khả năng mở rộng và ra quyết định kỹ thuật kèm đánh đổi. · skills: api-design, backend-patterns · tags: Lập trình, Kiến trúc
- **Người sửa lỗi build** (`ecc-build-error-resolver`) - Sửa lỗi build và lỗi kiểu TypeScript bằng thay đổi nhỏ nhất, không đụng kiến trúc. · skills: verification-loop · tags: Lập trình, Gỡ lỗi
- **Người review code** (`ecc-code-reviewer`) - Review code vừa viết về chất lượng, bảo mật và độ dễ bảo trì, xếp phát hiện theo mức nghiêm trọng. · skills: coding-standards, ecc-security-review · tags: Lập trình, Review
- **Người đơn giản hoá code** (`ecc-code-simplifier`) - Làm code vừa sửa gọn, rõ, nhất quán hơn mà không đổi hành vi. · skills: coding-standards · tags: Lập trình, Review
- **Người review database** (`ecc-database-reviewer`) - Soát truy vấn, schema, migration và bảo mật PostgreSQL, đề xuất index và cách sửa. · skills: postgres-patterns, database-migrations · tags: Lập trình, Database
- **Người cập nhật tài liệu** (`ecc-doc-updater`) - Cập nhật README, hướng dẫn và bản đồ code cho khớp với code hiện tại. · skills: codebase-onboarding · tags: Lập trình, Tài liệu
- **Người tra tài liệu** (`ecc-docs-lookup`) - Tra tài liệu mới nhất của thư viện, framework hay API (qua Context7) rồi trả lời kèm ví dụ. · tags: Lập trình, Tài liệu
- **Người chạy test E2E** (`ecc-e2e-runner`) - Viết, chạy và bảo trì test end-to-end bằng trình duyệt cho các luồng người dùng quan trọng. · skills: e2e-testing · tags: Lập trình, Kiểm thử
- **Người tối ưu hiệu năng** (`ecc-performance-optimizer`) - Tìm nút thắt, tối ưu code chậm, giảm kích thước bundle và cải thiện tốc độ chạy. · tags: Lập trình, Hiệu năng
- **Người lập kế hoạch** (`ecc-planner`) - Chia một tính năng hay đợt refactor lớn thành kế hoạch từng bước có rủi ro, phụ thuộc và cách kiểm. · skills: search-first, codebase-onboarding · tags: Lập trình, Kế hoạch
- **Người review Python** (`ecc-python-reviewer`) - Review code Python về PEP 8, type hint, bảo mật, hiệu năng và cách viết đúng chất Python. · skills: python-patterns, python-testing · tags: Lập trình, Review
- **Người review React** (`ecc-react-reviewer`) - Review component React về hook, hiệu năng render, ranh giới server/client và khả năng tiếp cận. · skills: frontend-patterns · tags: Lập trình, Review
- **Người dọn code chết** (`ecc-refactor-cleaner`) - Tìm và gỡ code không dùng, code trùng, dependency thừa bằng công cụ phân tích rồi kiểm lại. · skills: verification-loop · tags: Lập trình, Bảo trì
- **Người soát bảo mật** (`ecc-security-reviewer`) - Tìm và sửa lỗ hổng bảo mật ở chỗ xử lý đầu vào, xác thực, API, bí mật và thanh toán. · skills: ecc-security-review · tags: Lập trình, Bảo mật
- **Người săn lỗi bị nuốt** (`ecc-silent-failure-hunter`) - Tìm chỗ lỗi bị nuốt im lặng, fallback sai và lỗi không được truyền lên. · skills: error-handling · tags: Lập trình, Review
- **Người dẫn TDD** (`ecc-tdd-guide`) - Bắt viết test trước khi viết code cho tính năng mới, sửa lỗi hay refactor, giữ độ phủ test. · skills: tdd-workflow, python-testing · tags: Lập trình, Kiểm thử
- **Người review TypeScript** (`ecc-typescript-reviewer`) - Review code TypeScript/JavaScript về an toàn kiểu, async, bảo mật Node và web. · skills: coding-standards, backend-patterns · tags: Lập trình, Review
- **Dịch và bản địa hoá** (`tl-dich-ban-dia`) - Chuyển nội dung marketing giữa tiếng Việt và tiếng Anh, giữ nguyên sức bán chứ không dịch từng chữ. · skills: humanizer, notes
- **Người giải thích** (`tl-giai-thich`) - Bóc một khái niệm khó thành thứ hiểu được, kiểm lại xem đã hiểu thật chưa. · skills: grounded-citations, query-wiki
- **Trợ lý nghiên cứu** (`tl-nghien-cuu`) - Đào một chủ đề tới nơi, trả lời có trích dẫn, rồi nạp thứ đáng giữ vào Second Brain. · skills: grounded-citations, ingest-source, query-wiki, notes
- **Người phản biện** (`tl-phan-bien`) - Soi một kế hoạch hoặc ý tưởng để tìm chỗ sẽ hỏng, trước khi tiền và thời gian đổ vào. · skills: grounded-citations, verification-before-completion, query-wiki
- **Người rà soát RBAC** (`tl-ra-soat-rbac`) - Review manifest RBAC, NetworkPolicy và code tạo ServiceAccount/token, tìm chỗ leo thang quyền hoặc rò credential trước khi deploy. · tags: DevOps, Bảo mật
- **Thư ký** (`tl-thu-ky`) - Dọn hộp thư, đọc lịch, và sắp lại việc trong ngày theo thứ tự nên làm. · skills: email-inbox-triage, weekly-review-planning, query-wiki, notes
- **Kỹ sư tối ưu tài nguyên K8s** (`tl-toi-uu-tai-nguyen-k8s`) - Đọc số liệu CPU/RAM từ Prometheus và values ArgoCD, đề xuất chỉnh request/limit/HPA/min replicas cho fsel-prod, có số liệu và chỗ sửa cụ thể. · skills: bao-cao-tai-nguyen-k8s-prometheus · tags: DevOps, Vận hành
- **Người tóm tắt** (`tl-tom-tat`) - Biến tài liệu dài, biên bản họp hay chuỗi tin nhắn thành quyết định và việc cần làm. · skills: document-to-action-items, meeting-action-items, notes

## Skills
### AI
- **Ingest Source** (`ingest-source`) - Tiêu hoá một source thô vào Second Brain, chưng cất thành tri thức wiki tích luỹ.
- **Javis Builder** (`javis-builder`) - Tạo hoặc sửa năng lực của Javis: agent, skill, workflow, loop, plugin. Kèm mẫu file chuẩn và luật chống trùng.
- **Lập kế hoạch chi phí và lịch trình chuyến xe** (`lap-ke-hoach-chi-phi-va-lich-trinh-chuyen-xe`) - Tính quãng đường, chi phí thuê xe, nhiên liệu, phí đường bộ và lịch sạc cho chuyến đi.
- **Lint Wiki** (`lint-wiki`) - Rà soát sức khoẻ wiki của Second Brain, trả về danh sách vấn đề. Không tự sửa hàng loạt.
- **Notes** (`notes`) - Lưu tin nhắn hiện tại nguyên văn vào sources/ (kèm ảnh), tự chưng cất lên wiki nếu note đáng.
- **Query Wiki** (`query-wiki`) - Khai thác tri thức trong Second Brain: tổng hợp, so sánh, giả thuyết. Trả lời có trích dẫn.
### Chung
- **ask-matt** (`ask-matt`) - Ask which skill or flow fits your situation. A router over the skills in this repo.
- **brainstorming** (`brainstorming`) - You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it (a talk, a business, a renovation).
- **code-review** (`code-review`) - Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
- **codebase-design** (`codebase-design`) - Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.
- **diagnosing-bugs** (`diagnosing-bugs`) - Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
- **diagnosing-superpowers** (`diagnosing-superpowers`) - Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, "it took too long", "why is it so expensive", "what is it doing" — or wants to build a bug report for the superpowers maintainers, for the current session or a past one identified by id or path, on any harness.
- **dispatching-parallel-agents** (`dispatching-parallel-agents`) - Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
- **domain-modeling** (`domain-modeling`) - Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR.
- **executing-plans** (`executing-plans`) - Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available
- **finishing-a-development-branch** (`finishing-a-development-branch`) - Use when implementation is complete, all tests pass, and you need to decide how to integrate the work
- **grill-me** (`grill-me`) - A relentless interview to sharpen a plan or design.
- **grill-with-docs** (`grill-with-docs`) - A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
- **grilling** (`grilling`) - Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
- **handoff** (`handoff`) - Compact the current conversation into a handoff document for another agent to pick up.
- **implement** (`implement`) - Implement a piece of work based on a spec or set of tickets.
- **implement-spec** (`implement-spec`) - Implement the result of /to-spec and /to-tickets in code.
- **improve-codebase-architecture** (`improve-codebase-architecture`) - Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **pr** (`pr`) - Use when writing a PR body.
- **prototype** (`prototype`) - Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
- **receiving-code-review** (`receiving-code-review`) - Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation
- **research** (`research`) - Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
- **retro** (`retro`) - Conduct a retrospective on a coding session.
- **setup-matt-pocock-skills** (`setup-matt-pocock-skills`) - Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use of the other engineering skills.
- **requesting-code-review** (`sp-requesting-code-review`) - Use when completing tasks, implementing major features, or before merging to verify work meets requirements
- **systematic-debugging** (`sp-systematic-debugging`) - Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
- **test-driven-development** (`sp-test-driven-development`) - Use when implementing any feature or bugfix, before writing implementation code
- **subagent-driven-development** (`subagent-driven-development`) - Use when executing implementation plans with independent tasks in the current session
- **tdd** (`tdd`) - Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
- **teach** (`teach`) - Teach the user a new skill or concept, within this workspace.
- **to-questionnaire** (`to-questionnaire`) - Turn a decision you can't fully answer into a questionnaire for someone else to fill in.
- **to-spec** (`to-spec`) - Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed.
- **to-tickets** (`to-tickets`) - Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
- **triage** (`triage`) - Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs.
- **using-git-worktrees** (`using-git-worktrees`) - Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback
- **using-superpowers** (`using-superpowers`) - Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
- **verification-before-completion** (`verification-before-completion`) - Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
- **wait-what** (`wait-what`) - Stop. That last message did not land: re-pitch it.
- **wayfinder** (`wayfinder`) - Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
- **wizard** (`wizard`) - Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.
- **writing-for-agents** (`writing-for-agents`) - Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md.
- **writing-plans** (`writing-plans`) - Use when you have a spec or requirements for a multi-step task, before touching code
- **writing-skills** (`writing-skills`) - Use when creating new skills, editing existing skills, or verifying skills work before deployment
### DevOps
- **Báo cáo tài nguyên K8s qua Prometheus** (`bao-cao-tai-nguyen-k8s-prometheus`) - Thống kê CPU/RAM request/usage của node pool và service K8s từ Prometheus, gửi Slack, đề xuất chỉnh request/limit/HPA.
- **Chẩn đoán pod CrashLoopBackOff** (`chan-doan-pod-crashloop`) - Tìm nguyên nhân pod Kubernetes CrashLoopBackOff qua log container đã chết, secret, quyền volume và kết nối DB, chỉ dùng lệnh đọc.
- **Kiểm thử kubeconfig dev** (`kiem-thu-kubeconfig-dev`) - Kiểm chứng kubeconfig dev do kubeconfig-generator cấp: quyền theo namespace, hết hạn, revoke, tài nguyên mồ côi, bằng kubectl.
- **Kiểm tra pod thấp so với request** (`kiem-tra-pod-thap-so-request`) - Liệt kê pod Kubernetes có CPU và RAM usage dưới ngưỡng phần trăm của request, gộp theo service.
- **Quét secret trước commit** (`quet-secret-truoc-commit`) - Quét các file đã stage tìm cert, private key, JWT, token dài và Slack webhook trước khi commit repo.
- **Sửa key Secret không lộ giá trị** (`sua-key-secret-khong-lo-gia-tri`) - Sửa một key trong Kubernetes Secret bằng kubectl patch mà không in giá trị ra chat, kèm kiểm độ dài sau khi sửa.
### Marketing
- **HTML sang Webcake** (`html-to-webcake`) - Chuyển trang HTML thành file .pke mở được trong trình dựng Webcake, giữ đúng màu, cỡ chữ, ảnh và bố cục của bản gốc.

## Workflows
- **Dựng công cụ cấp kubeconfig** (`dung-cong-cu-cap-kubeconfig`) - off · 3 bước [tl-phan-bien -> tl-ra-soat-rbac -> tl-thu-ky] · Cổng soát cho kubeconfig-generator. Phản biện, rà RBAC rồi gom việc còn mở; chạy trước khi viết code và sau khi code xong.

## Loops
- **Tổng hợp kiến thức** (`tong-hop-kien-thuc`) - bật · custom/full · mỗi 960 phút

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

## Cờ sức khoẻ
- Agent chưa workflow nào dùng: ecc-architect, ecc-build-error-resolver, ecc-code-reviewer, ecc-code-simplifier, ecc-database-reviewer, ecc-doc-updater, ecc-docs-lookup, ecc-e2e-runner, ecc-performance-optimizer, ecc-planner, ecc-python-reviewer, ecc-react-reviewer, ecc-refactor-cleaner, ecc-security-reviewer, ecc-silent-failure-hunter, ecc-tdd-guide, ecc-typescript-reviewer, tl-dich-ban-dia, tl-giai-thich, tl-nghien-cuu, tl-toi-uu-tai-nguyen-k8s, tl-tom-tat
