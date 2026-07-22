# BÁO CÁO THỰC HÀNH PYTHON

## BÀI THỰC HÀNH 01: Khởi tạo dự án Employee Task Scheduler bằng Python Flask và GitHub

**1. Thông tin nhóm**
- **Mã nhóm:** Nhóm [Điền số nhóm]
- **Tên dự án:** Employee Task Scheduler (bt lam web)
- **Lớp:** [Điền tên lớp]
- **Ngày thực hiện:** 22/07/2026
- **Thành viên:**
  1. Trần Thanh Bình (Nhóm trưởng)
  2. [Tên thành viên 2]
  3. [Tên thành viên 3]
  4. [Tên thành viên 4]
  5. [Tên thành viên 5]
  6. [Tên thành viên 6]

---

**2. Kết quả thực hành**

*(Hướng dẫn: Bạn hãy chụp ảnh màn hình và dán (Paste) đè lên các dòng chữ in nghiêng dưới đây)*

**2.1. Cấu trúc Project trong VS Code/Cursor:**
*[Dán ảnh chụp màn hình danh sách file/thư mục bên trái màn hình VS Code vào đây]*

**2.2. Cửa sổ Terminal khi chạy lệnh chạy server:**
*[Dán ảnh chụp màn hình cửa sổ Terminal đen có dòng chữ "Running on http://127.0.0.1:5000" vào đây]*

**2.3. Giao diện Web hiển thị trên trình duyệt:**
*[Dán ảnh chụp trang Dashboard của web (đã có màu nền xám, chữ "bt lam web") vào đây]*

**2.4. GitHub Repository sau khi Push thành công:**
*[Dán ảnh chụp trang web GitHub có các file mã nguồn vào đây]*

**2.5. Lịch sử Commit đầu tiên:**
*[Dán ảnh chụp phần lịch sử (Commits) trên GitHub có chữ "Khởi tạo dự án cấu trúc cơ bản và giao diện UI" vào đây]*

---

**3. Phân công công việc**

| Thành viên | Công việc thực hiện | Tỷ lệ đóng góp (%) |
|------------|---------------------|--------------------|
| SV1 (Trần Thanh Bình) | Khởi tạo dự án, Cài đặt Flask, GitHub Repo, Thiết kế UI | 100% |
| SV2 | [Ghi công việc] | [X]% |
| SV3 | [Ghi công việc] | [X]% |
| SV4 | [Ghi công việc] | [X]% |
| SV5 | [Ghi công việc] | [X]% |
| SV6 | [Ghi công việc] | [X]% |

---

**4. Khó khăn gặp phải**
- **Mô tả lỗi:** Khi khởi chạy Server, môi trường Python gốc trong máy bị xung đột (biến môi trường PYTHONHOME) khiến Terminal bị tắt ngang, web báo "refused to connect". Lỗi push GitHub do chưa cấu hình tên/email.
- **Cách nhóm giải quyết:** Viết một file `.bat` (KhoiDongWeb.bat) để tự động xóa biến PYTHONHOME và kích hoạt ảo (venv) trước khi chạy Server. Khởi tạo `git config --global` để thiết lập email trước khi commit.

---

**5. Tự đánh giá**
- **Điều đã làm được:** 
  - Khởi tạo thành công dự án bằng Flask, phân chia kiến trúc Blueprint (routes, models, templates).
  - Kết nối CSDL SQLite thành công bằng SQLAlchemy.
  - Thiết kế được giao diện cực kỳ hiện đại với Bootstrap 5, có Dark mode.
  - Làm xong toàn bộ **Bài tập mở rộng**: Tạo trang `/about`, đổi màu nền CSS, thanh điều hướng Navbar.
  - Push code lên GitHub thành công.
- **Điều cần cải thiện:** Cần tìm hiểu sâu hơn về quy trình chia nhánh (Branch) và Pull Request trên GitHub để các bạn trong nhóm ghép code dễ hơn.
- **Kế hoạch buổi tiếp theo:** Bắt tay vào làm chi tiết các module Quản lý Nhân viên và Phân công (Milestone 2).

