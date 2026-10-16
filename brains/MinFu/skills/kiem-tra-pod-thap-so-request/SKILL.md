---
name: "Kiểm tra pod thấp so với request"
description: "Liệt kê pod Kubernetes có CPU và RAM usage dưới ngưỡng phần trăm của request, gộp theo service."
group: "DevOps"
origin: javis-learned
status: active
created: 2026-10-14
---
## Khi nào dùng
- Người dùng hỏi pod nào request quá cao so với mức dùng, hoặc muốn giảm request/replica trong một namespace.

## Quy trình
1. Lấy usage hiện tại của từng pod bằng kubectl top trong namespace cần xem.
2. Đọc request CPU và RAM của từng container từ spec của pod hoặc deployment.
3. Tính tỉ lệ usage/request cho CPU và RAM, làm tròn một chữ số thập phân.
4. Lọc pod có CPU VÀ RAM cùng dưới ngưỡng (mặc định 10%). Chỉ một trong hai chưa đủ điều kiện.
5. Gộp kết quả theo service (tên deployment, bỏ phần hash của pod) và đếm số pod mỗi service.
6. Ghi rõ thời điểm lấy số và nói rõ đó là mẫu tức thời, không phải trung bình.

## Bẫy
- Pod chưa có số liệu usage thì loại khỏi phép tính và nêu tên riêng, không coi là 0%.
- Một lần đo không đại diện cho giờ cao điểm. Trước khi đề xuất giảm request, hỏi người dùng có số liệu cao điểm không.
- Chỉ báo cáo và đề xuất. Không tự sửa request, replica hay manifest.

## Kiểm chứng
- Số pod được lọc ra phải khớp số dòng trong bảng kết quả.
- Mỗi pod trong bảng có đủ giá trị usage và request của cả CPU lẫn RAM.
