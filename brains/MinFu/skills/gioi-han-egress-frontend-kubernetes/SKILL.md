---
name: "Giới hạn Egress frontend Kubernetes"
description: "Thiết kế và kiểm tra NetworkPolicy để giới hạn kết nối đi ra của pod frontend trong Kubernetes."
group: "DevOps"
origin: javis-learned
status: active
created: 2026-11-11
---
## Khi nào dùng
- Khi cần hạn chế pod frontend gọi tới database hoặc các đích mạng không cần thiết.
- Khi cần kiểm tra một NetworkPolicy Egress trước khi áp dụng vào cluster.

## Chuẩn bị
- Xác định cluster context và namespace đích.
- Kiểm tra CNI và các NetworkPolicy đang áp dụng cho pod mục tiêu.
- Liệt kê các luồng frontend cần dùng, gồm DNS, gateway, API, dịch vụ nội bộ và đích bên ngoài.
- Xác định pod frontend bằng nhãn riêng của ứng dụng. Không chọn bằng nhãn dùng chung với backend.

## Cách chạy
1. Đọc manifest hiện có và xác định chính xác pod nào sẽ bị chọn.
2. Lập danh sách đích cần cho phép trước khi đặt chính sách chặn mặc định.
3. Thiết kế Egress theo nguyên tắc chỉ cho phép các luồng cần thiết.
4. Kiểm tra manifest bằng server-side dry-run trước khi áp dụng.
5. Chỉ áp dụng sau khi người dùng yêu cầu hoặc duyệt việc áp dụng.

## Quy trình
1. Kiểm tra cluster context, namespace, CNI và các policy đang tồn tại.
2. Kiểm tra nhãn thực tế của pod frontend và đối chiếu selector dự kiến.
3. Xác định đích database, cache, proxy, gateway, DNS và API mà ứng dụng cần truy cập.
4. Chú ý database có thể được truy cập qua proxy hoặc NodePort với cổng khác, không chỉ qua cổng database trực tiếp.
5. Tạo policy Egress chọn đúng nhóm pod frontend.
6. Cho phép DNS và từng đích ứng dụng thực sự cần, với protocol và port phù hợp.
7. Không thêm rule cho database, Redis, HAProxy hoặc đích khác nếu mục tiêu là chặn các đường truy cập đó.
8. Rà soát các NetworkPolicy khác cùng chọn nhóm pod. Quyền cho phép từ nhiều policy có thể cộng dồn.
9. Kiểm tra manifest bằng `kubectl --context=<context> apply --dry-run=server -f <manifest>`.
10. Trình bày rõ pod được chọn, luồng được phép, luồng dự kiến bị chặn và phạm vi tác động.
11. Sau khi được áp dụng, kiểm tra DNS, giao diện, chức năng gọi API và các kết nối mới tới database qua mọi đường truy cập đã biết.
12. Ghi lại lệnh hoàn tác phù hợp với tên policy và namespace thực tế.
13. Nếu frontend chỉ phục vụ HTML/JavaScript chạy trong trình duyệt, giải thích rằng Egress policy của pod không kiểm soát các kết nối do máy người dùng tạo ra.

## Bẫy
- Nhãn chung giữa frontend và backend có thể khiến policy chọn nhầm workload.
- Chỉ chặn cổng database trực tiếp có thể bỏ sót đường qua proxy hoặc NodePort.
- Default deny Egress có thể làm hỏng DNS hoặc các API mà ứng dụng cần.
- Một policy khác có thể tiếp tục cho phép lưu lượng tới cùng nhóm pod.
- Kiểm tra dry-run xác nhận API server chấp nhận manifest, không chứng minh lưu lượng thực tế đã bị chặn.
- Policy Egress không tự giới hạn chiều vào pod.

## Kiểm chứng
- Xác nhận selector khớp đúng các pod frontend và không khớp backend.
- Xác nhận các luồng cần thiết vẫn hoạt động sau khi áp dụng.
- Thử kết nối mới tới database bằng đường trực tiếp và các proxy hoặc cổng trung gian đã biết.
- Phân biệt kết quả kiểm tra manifest với kết quả kiểm tra mạng thực tế.
