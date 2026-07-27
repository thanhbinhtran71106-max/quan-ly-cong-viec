import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule

app = create_app()

def seed_data():
    with app.app_context():
        print("Bắt đầu dọn dẹp lịch cũ...")
        Schedule.query.delete()
        Employee.query.delete()
        Task.query.delete()
        db.session.commit()

        print("Thêm danh sách nhân viên công ty...")
        employees_data = [
            ("Lý Mỹ Duyên", "Kinh doanh", "NV001"),
            ("Vương Nhật Minh", "Kinh doanh", "NV002"),
            ("Đào Thanh Trúc", "Kế toán", "NV003"),
            ("Trần Quang Khải", "IT Support", "NV004"),
            ("Trịnh Thu Phương", "Kế toán", "NV005"),
            ("Bùi Văn Hoàng", "Hành chính", "NV006"),
            ("Nguyễn Hải Đăng", "Kỹ thuật", "NV007"),
            ("Phạm Thùy Linh", "Kinh doanh", "NV008"),
            ("Lê Hoàng Long", "Kỹ thuật", "NV009"),
            ("Cao Tuấn Tú", "IT Support", "NV010"),
            ("Đỗ Thị Mỹ Linh", "Hành chính", "NV011"),
            ("Ngô Bảo Châu", "Nhân sự", "NV012"),
        ]
        
        employees = []
        for fullname, dept, code in employees_data:
            email = f"{code.lower()}@company.com"
            phone = f"09{random.randint(10000000, 99999999)}"
            position = "Nhân viên"
            emp = Employee(fullname=fullname, department=dept, code=code, email=email, phone=phone, position=position)
            db.session.add(emp)
            employees.append(emp)
            
        print("Thêm danh sách công việc...")
        tasks_data = [
            ("Kiểm tra báo cáo", "Kinh doanh", "Cao"),
            ("Bảo trì hệ thống", "IT Support", "Cao"),
            ("Xử lý CV ứng viên", "Nhân sự", "Trung bình"),
            ("Họp nhóm doanh số", "Kinh doanh", "Cao"),
            ("Báo cáo tài chính", "Kế toán", "Cao"),
            ("Cập nhật phần mềm", "Kỹ thuật", "Trung bình"),
            ("Đối chiếu công nợ", "Kế toán", "Trung bình"),
            ("Mua sắm thiết bị", "Hành chính", "Thấp"),
            ("Tư vấn khách hàng", "Kinh doanh", "Trung bình"),
            ("Lắp đặt mạng", "IT Support", "Trung bình"),
            ("Kiểm tra sản phẩm", "Kỹ thuật", "Cao"),
            ("Tổ chức sự kiện", "Hành chính", "Thấp"),
        ]
        
        tasks = []
        for i, (name, dept, priority) in enumerate(tasks_data):
            task = Task(task_name=name, required_expertise=dept, priority=priority, code=f"CV{i+1:03d}")
            db.session.add(task)
            tasks.append(task)
            
        db.session.commit()

        print("Tạo lịch ngẫu nhiên cho tuần hiện tại...")
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        shifts = ['Sáng', 'Chiều']
        
        for emp in employees:
            # Mỗi nhân viên làm khoảng 3-5 ngày trong tuần
            working_days = random.sample(range(6), random.randint(3, 5))
            for day in working_days:
                sched_date = start_of_week + timedelta(days=day)
                
                # Sáng
                if random.random() > 0.3: # 70% có việc sáng
                    # Pick a random task matching department or without
                    dept_tasks = [t for t in tasks if t.required_expertise == emp.department]
                    if dept_tasks:
                        sched = Schedule(
                            employee_id=emp.id,
                            task_id=random.choice(dept_tasks).id,
                            date=sched_date,
                            shift='Sáng',
                            status=random.choice(['Todo', 'In Progress', 'Done'])
                        )
                        db.session.add(sched)
                
                # Chiều
                if random.random() > 0.4: # 60% có việc chiều
                    dept_tasks = [t for t in tasks if t.required_expertise == emp.department]
                    if dept_tasks:
                        sched = Schedule(
                            employee_id=emp.id,
                            task_id=random.choice(dept_tasks).id,
                            date=sched_date,
                            shift='Chiều',
                            status=random.choice(['Todo', 'In Progress', 'Done'])
                        )
                        db.session.add(sched)
                        
        db.session.commit()
        print("Tạo dữ liệu giả lập thành công!")

if __name__ == '__main__':
    seed_data()
