# Hệ Thống IoT Giám Sát Cảm Biến & Điều Khiển Thiết Bị ESP32

Ứng dụng giám sát thiết bị cảm biến nhiệt độ, độ ẩm và điều khiển quạt gió tự động bằng AI (Autopilot) & Chatbot hỗ trợ, được phát triển trên quy trình Agile Scrum.

## Yêu cầu môi trường
- Python 3.10 trở lên
- Trình duyệt web (Chrome/Edge/Firefox)

## Hướng dẫn cài đặt và chạy
1. Truy cập thư mục:
   ```bash
   cd app-dieu-khien
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```bash
   python run.py
   ```
   > Hệ thống sẽ tự động tạo cơ sở dữ liệu `aiot_v2.db` và nạp sẵn dữ liệu thiết bị (ESP32, STM32), cảm biến cùng tài khoản quản trị mẫu (`admin` / `admin123`).

---

## 📋 Phân Chia Công Việc Thành Viên (Sprint Task Board)

Dưới đây là bảng phân công vai trò và chi tiết các đầu việc đã thực hiện của từng thành viên trong nhóm, tương ứng với quy trình phân tách Agile Scrum:

| Thành viên | Vai trò | Công việc đã thực hiện (Sprint 1 & 2) | Trạng thái |
| :--- | :--- | :--- | :--- |
| **Trần Thanh Bình** | **Project Manager (PM) & QA** | - Quản trị dự án, lập kế hoạch các Sprint.<br>- Kiểm thử toàn bộ giao diện và chức năng phản hồi hệ thống (QA).<br>- Tối ưu hóa tệp khởi chạy hệ thống `run.py` và luồng chạy thực tế. | `[x] Hoàn thành` |
| **The Romen** | **Backend & AI Developer** | - Thiết kế mô hình CSDL nâng cấp (`models.py`, `repositories.py`).<br>- Xây dựng API cảm biến, API trích xuất CSV dữ liệu và API xác thực kép.<br>- Phát triển thuật toán AI dự báo xu hướng nhiệt độ và chế độ điều khiển tự động Autopilot.<br>- Cấu hình dịch vụ MQTT lắng nghe và đồng bộ dữ liệu cảm biến thực tế. | `[x] Hoàn thành` |
| **Thien** | **Frontend & UI/UX Developer** | - Thiết kế giao diện Dashboard theo phong cách Glassmorphism.<br>- Tích hợp SocketIO phía Client để tự động bật/tắt quạt và hạ nhiệt độ thời gian thực.<br>- Thiết kế widget Chatbot AI ở góc phải màn hình kèm bong bóng trả lời nhanh (Quick Replies).<br>- Dựng giao diện hộp thoại Profile thông tin nhân viên và Đổi mật khẩu. | `[x] Hoàn thành` |

---

## 🛠️ Tính năng nổi bật
- **AI Autopilot**: Tự động dự đoán nhiệt độ và kích hoạt hệ thống quạt thông gió làm mát.
- **AI Chatbot**: Trợ lý AI tích hợp sẵn các bong bóng trả lời nhanh và hỗ trợ ra lệnh điều khiển bằng giọng thoại tự nhiên.
- **Bảng hiệu chuẩn**: Cho phép quản trị viên hiệu chỉnh sai số của từng cảm biến.
