---
type: workflow
name: Dựng công cụ cấp kubeconfig
slug: dung-cong-cu-cap-kubeconfig
status: 'off'
group: DevOps
description: Cổng soát cho kubeconfig-generator. Phản biện, rà RBAC rồi gom việc còn mở; chạy trước khi viết code và sau khi code xong.
steps:
  - agent: tl-phan-bien
    task: "Soi đầu vào sau theo bốn hướng của bạn (giả định ngầm, hỏng ở đâu trước, chi phí bỏ sót, cách rẻ hơn). Đầu vào là đặc tả và kiến trúc, hoặc code/diff của kubeconfig-generator. Tập trung vào: giới hạn TokenRequest trên FKE 1.25, đường mạng từ fsel-local tới API server fsel-prod, danh tính từ oauth2-proxy, label hợp lệ, dọn dẹp khi lỗi giữa chừng.\n\n{{input}}"
  - agent: tl-ra-soat-rbac
    task: "Rà RBAC, NetworkPolicy, code tạo SA/RoleBinding/token và xử lý credential trong đầu vào dưới đây, đối chiếu đặc tả prompt-cong-cu-cap-kubeconfig.md mục 4 và 7. Coi nhận xét của người phản biện là gợi ý, tự kiểm lại.\n\nĐẦU VÀO:\n{{input}}\n\nNHẬN XÉT PHẢN BIỆN:\n{{prev}}"
  - agent: tl-thu-ky
    task: "Từ kết quả rà soát dưới đây, lập danh sách việc còn mở cho kubeconfig-generator: (1) lỗi phải sửa trước khi deploy, (2) điểm chủ cần chốt, (3) việc để sau. Mỗi mục một dòng, ghi nguồn (phản biện hay rà RBAC). Không thêm việc mới ngoài kết quả.\n\n{{prev}}"
updated: 2026-10-23
---

# Dựng công cụ cấp kubeconfig

Quy trình đầy đủ có 6 bước. Ba bước tự động ở trên là **cổng soát**, chạy hai lần: một lần trước khi viết code (đầu vào là đặc tả và kiến trúc), một lần sau khi code xong (đầu vào là diff hoặc nội dung file).

| Bước | Ai làm | Ghi chú |
|---|---|---|
| 1. Soi đặc tả | `tl-phan-bien` | Cổng soát, lần 1 |
| 2. Đề xuất kiến trúc | Engine chính (trong chat) | **Dừng chờ chủ duyệt.** Không viết code khi chưa duyệt |
| 3. Viết code và test | Engine chính (trong chat) | Repo `D:\FSEL\other-services\kubeconfig-generator`, push thẳng `main` |
| 4. Rà RBAC và bảo mật | `tl-ra-soat-rbac` | Cổng soát, lần 2, đầu vào là diff |
| 5. Kiểm thử trên cluster | Skill `kiem-thu-kubeconfig-dev` | fsel-local, namespace test chủ chỉ định |
| 6. Tóm tắt việc còn mở | `tl-thu-ky` | Bước cuối của cổng soát |

## Vì sao bước 2, 3, 5 không nằm trong `steps`
- Agent chạy nền chỉ đọc được brain, không đọc hay ghi được repo ở `D:\FSEL`, và không được push. Nên viết code và push phải làm trong chat.
- Workflow chạy một mạch, không có điểm dừng chờ duyệt. Dừng ở bước 2 được giữ bằng cách tách: cổng soát lần 1 xong thì chủ duyệt trong chat, rồi mới sang bước 3.
- Bước 5 cần namespace test và tạo SA thật, nên chạy trong chat khi chủ đã cho tên namespace.

## Đầu vào gợi ý
- Lần 1: nội dung `prompt-cong-cu-cap-kubeconfig.md` cộng bản đề xuất kiến trúc.
- Lần 2: `git diff` hoặc nội dung các file `deploy/rbac-*.yaml`, `deploy/networkpolicy.yaml`, `app/k8s.py`, `app/auth.py`, `app/download.py`, `tests/`.

## Quy tắc
- Không commit kubeconfig admin, `.env`, token. Secret truyền qua Secret của K8s.
- Lỗi mức Nghiêm trọng hoặc Cao từ `tl-ra-soat-rbac` phải sửa xong mới push bản deploy.
