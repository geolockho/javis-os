---
type: wiki
status: active
tags: [wiki]
origin: javis-learned
created: 2026-11-11
updated: 2026-11-11
source: [[conversations/2026-11-11]]
---
## Job trong cùng stage

Các job trong cùng stage có thể chạy đồng thời, nhưng số runner và khả năng nhận job ảnh hưởng thời điểm chúng thực sự bắt đầu. [[Tài liệu GitLab về stages]]

Một job thất bại không tự làm các job khác trong cùng stage thất bại theo. Pipeline có thể chuyển sang trạng thái thất bại dù các job cùng stage vẫn hoàn tất. [[Tài liệu GitLab về stages]]

## Chuyển sang stage sau

Theo thứ tự stage thông thường, stage tiếp theo chỉ chạy sau khi các job ở stage hiện tại hoàn tất thành công; nếu có job bắt buộc thất bại, các job ở stage sau thường bị bỏ qua và pipeline thất bại. [[Tài liệu GitLab về stages]]

`allow_failure: true` có thể cho phép pipeline tiếp tục sau khi job lỗi. `when: always` có thể chạy job bất kể trạng thái stage trước, còn `needs` có thể cho job phụ thuộc chạy khi các job được khai báo hoàn tất mà không cần đợi toàn bộ stage. [[Tài liệu GitLab về allow_failure]], [[Tài liệu GitLab về when]], [[Tài liệu GitLab về needs]]
