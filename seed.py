from app import create_app, db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # 1. Thêm Nhân Viên
    emps = [
        Employee(code='NV001', fullname='Nguyễn Văn Nam', email='nam.nv@congty.com', phone='0901234561', department='IT Support', position='Chuyên viên', base_salary_per_hour=80000),
        Employee(code='NV002', fullname='Trần Thị Bình', email='binh.tt@congty.com', phone='0901234562', department='Kinh doanh', position='Nhân viên Sale', base_salary_per_hour=60000),
        Employee(code='NV003', fullname='Lê Hoàng Phúc', email='phuc.lh@congty.com', phone='0901234563', department='Hành chính', position='Nhân viên Văn phòng', base_salary_per_hour=50000),
        Employee(code='NV004', fullname='Phạm Minh Khang', email='khang.pm@congty.com', phone='0901234564', department='Kỹ thuật', position='Kỹ sư Mạng', base_salary_per_hour=100000),
    ]
    db.session.add_all(emps)

    # 2. Thêm Công Việc
    tasks = [
        Task(code='CV001', task_name='Sửa lỗi máy chủ Web', priority='Cao', duration=4, required_expertise='IT Support', description='Kiểm tra và cấu hình lại Nginx'),
        Task(code='CV002', task_name='Lập trình tính năng mới', priority='Cao', duration=6, required_expertise='IT Support', description='Code backend API bằng Python'),
        Task(code='CV003', task_name='Gặp gỡ khách hàng VIP', priority='Cao', duration=4, required_expertise='Kinh doanh', description='Đàm phán hợp đồng cung cấp phần mềm'),
        Task(code='CV004', task_name='Gọi điện tư vấn (Telesale)', priority='Trung bình', duration=4, required_expertise='Kinh doanh', description='Gọi danh sách 100 khách hàng tiềm năng'),
        Task(code='CV005', task_name='Soạn thảo Hợp đồng lao động', priority='Trung bình', duration=2, required_expertise='Hành chính', description='Soạn hợp đồng cho nhân viên mới'),
        Task(code='CV006', task_name='Sắp xếp hồ sơ lưu trữ', priority='Thường', duration=4, required_expertise='Hành chính', description='Phân loại hồ sơ năm 2026'),
    ]
    db.session.add_all(tasks)

    db.session.commit()
    print("Khởi tạo dữ liệu mẫu thành công!")
