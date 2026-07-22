# Employee Task Scheduler

Hệ thống quản lý và phân công công việc cho nhân viên theo tuần.

## Công nghệ sử dụng
- Python 3.10
- Flask 3.0.3
- SQLite & SQLAlchemy ORM
- HTML5, Bootstrap 5 (Giao diện)

## Cách cài đặt và chạy
1. Clone dự án về máy:
   ```bash
   git clone <link-github-cua-ban>
   cd employee_scheduler
   ```
2. Tạo môi trường ảo và cài đặt thư viện:
   ```bash
   python -m venv venv
   # Kích hoạt venv (Windows):
   .\venv\Scripts\activate
   # Cài đặt requirements
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```bash
   python run.py
   ```
   Ứng dụng sẽ chạy tại `http://127.0.0.1:5000/`. Lần đầu chạy sẽ tự động tạo CSDL `instance/scheduler.db` và dữ liệu mẫu.
