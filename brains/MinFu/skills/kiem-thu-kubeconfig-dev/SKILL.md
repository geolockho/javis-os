---
name: "Kiểm thử kubeconfig dev"
description: "Kiểm chứng kubeconfig dev do kubeconfig-generator cấp: quyền theo namespace, hết hạn, revoke, tài nguyên mồ côi, bằng kubectl."
group: "DevOps"
---

## Khi nào dùng
- "Kiểm thử kubeconfig vừa cấp", "test công cụ cấp kubeconfig trên fsel-local".
- Bước 5 của workflow `dung-cong-cu-cap-kubeconfig`, sau khi code đã qua review RBAC.
- Sau khi deploy bản mới của kubeconfig-generator, cần chạy lại nghiệm thu mục 7 trong `prompt-cong-cu-cap-kubeconfig.md`.

## Chuẩn bị
- Context admin: `fsel-local` trước. `fsel-prod` chỉ chạy các bước ĐỌC, trừ khi chủ cho phép rõ trong task.
- Namespace test do chủ chỉ định (gọi là `NS_A`) và một namespace khác để kiểm Forbidden (`NS_B`). Chưa có tên namespace thì DỪNG và hỏi, không tự chọn.
- File kubeconfig dev vừa tải từ tool, lưu tạm ngoài vault và ngoài repo, ví dụ `$env:TEMP\dev-kubeconfig.yaml`. Xoá file sau khi test.
- Label tool gắn lên tài nguyên: `app.kubernetes.io/managed-by=kubeconfig-generator` và `kubeconfig-generator/request-id=<id>`. Nếu code đổi key label thì sửa lệnh theo code, không theo file này.

## Quy trình
Đặt biến cho gọn (PowerShell):
```
$KC = "$env:TEMP\dev-kubeconfig.yaml"
$CTX = "fsel-local"
$NS_A = "<namespace test>"
$NS_B = "<namespace khác>"
$RID = "<request id>"
```

1. **Quyền đúng namespace**
   - `kubectl --kubeconfig $KC auth can-i list pods -n $NS_A` phải ra `yes`.
   - `kubectl --kubeconfig $KC get pods -n $NS_A` chạy được.
   - `kubectl --kubeconfig $KC auth can-i list pods -n $NS_B` phải ra `no`.
   - `kubectl --kubeconfig $KC get pods -n $NS_B` phải báo Forbidden.
2. **Đúng read-only**
   - `kubectl --kubeconfig $KC auth can-i --list -n $NS_A`: không được có verb create, update, patch, delete.
   - `kubectl --kubeconfig $KC auth can-i get secrets -n $NS_A` phải ra `no` (ClusterRole `view` không cho đọc secret).
3. **Tài nguyên tạo ra đúng phạm vi**
   - `kubectl --context $CTX get sa,rolebinding -n $NS_A -l kubeconfig-generator/request-id=$RID -o wide`: đúng 1 SA và 1 RoleBinding.
   - `kubectl --context $CTX get rolebinding -n $NS_A -l kubeconfig-generator/request-id=$RID -o jsonpath='{.items[*].roleRef.name}'` phải là `view`.
   - `kubectl --context $CTX get clusterrolebinding -l app.kubernetes.io/managed-by=kubeconfig-generator` phải rỗng.
4. **Thời hạn token** (không in token ra màn hình)
   - `python skills/kiem-thu-kubeconfig-dev/scripts/token_exp.py $KC` in ra `exp` và số giờ còn lại.
   - So với thời hạn tool hiển thị cho dev và cột hết hạn trong DB. Lệch quá 1 phút là lỗi.
5. **Token hết hạn**
   - Chỉ test được với token ngắn. API server không nhận `expirationSeconds` dưới 600 giây, nên cần cấu hình thời hạn ngắn nhất 10 phút ở môi trường test.
   - Đợi qua `exp` rồi chạy `kubectl --kubeconfig $KC get pods -n $NS_A`: phải báo Unauthorized.
6. **Revoke**
   - Admin bấm revoke trên tool.
   - `kubectl --context $CTX get sa,rolebinding -n $NS_A -l kubeconfig-generator/request-id=$RID` phải rỗng.
   - `kubectl --kubeconfig $KC get pods -n $NS_A` phải báo Unauthorized (xoá SA thì token gắn với SA mất hiệu lực).
7. **Không còn tài nguyên mồ côi**
   - `kubectl --context $CTX get sa,rolebinding -A -l app.kubernetes.io/managed-by=kubeconfig-generator` rồi đối chiếu từng request-id với DB: chỉ request còn hiệu lực mới được có tài nguyên.
8. **Dọn dẹp chỉ đụng tài nguyên của tool**
   - Trước khi chạy job dọn dẹp, tạo một SA mồi không có label managed-by trong `$NS_A`: `kubectl --context $CTX create sa decoy-khong-xoa -n $NS_A`.
   - Sau lượt dọn dẹp, SA mồi phải còn. Xoá SA mồi bằng tay khi xong.

## Bẫy
- `auth can-i` với `--kubeconfig` là hỏi bằng danh tính của dev. Quên `--kubeconfig` là hỏi bằng quyền admin và luôn ra `yes`.
- fsel-prod (FKE 1.25) có thể cắt ngắn thời hạn TokenRequest. Lấy thời hạn thật từ `exp` trong token, không tin thời hạn đã xin.
- Kubeconfig dev chứa token thật. Không dán vào chat, không lưu vào vault, không commit.
- Bước 8 tạo tài nguyên trên cluster. Chỉ làm trong namespace test chủ đã chỉ định.

## Kiểm chứng
Báo cáo dạng bảng: Bước | Lệnh | Kỳ vọng | Thực tế | ĐẠT/TRƯỢT. Ghi nguyên văn output lỗi (bỏ token nếu có). Bước nào không chạy được thì ghi lý do, không đánh ĐẠT.
