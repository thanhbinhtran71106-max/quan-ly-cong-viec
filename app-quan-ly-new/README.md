# Ứng dụng Quản lý Nhiệt độ & Quy tắc Tự động hóa (Phiên bản v2)

Đây là phiên bản tích hợp mới được giải nén từ file zip trên ổ D, chạy song song cùng hệ thống chính.

## Yêu cầu môi trường
- Python 3.10 trở lên
- Trình duyệt web (Chrome/Edge/Firefox)

## Hướng dẫn cài đặt và chạy
1. Truy cập thư mục:
   ```bash
   cd app-quan-ly-new/server
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r ../../app-dieu-khien/requirements.txt
   ```
3. Chạy ứng dụng:
   ```bash
   python app.py
   ```
   > Ứng dụng đã được cấu hình chạy trên cổng **`5001`** (để tránh xung đột với cổng `5000` của dự án chính).
4. Mở trình duyệt và truy cập: [http://localhost:5001](http://localhost:5001)

## Các tính năng chính trong phiên bản này
- **Auto Rules**: Quản lý các quy tắc tự động hóa (ví dụ: bật quạt khi nhiệt độ > 35°C, bật đèn khi ánh sáng < 20%).
- **LED Control**: Nút bật/tắt thiết bị đèn LED trực tuyến từ xa qua giao thức API.
- **Support Tickets**: Hệ thống gửi phiếu yêu cầu hỗ trợ kỹ thuật có trả phí (Paid Tickets).
- **Notifications**: Quản lý thông báo khẩn cấp thời gian thực của thiết bị.
- **Light Sensor**: Tích hợp thu thập dữ liệu cường độ ánh sáng của môi trường.
