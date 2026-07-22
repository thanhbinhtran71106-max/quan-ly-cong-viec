from app import create_app, db
from app.models import Employee, Task, Schedule

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Employee': Employee, 'Task': Task, 'Schedule': Schedule}


def seed_data():
    """Insert sample data if database is empty."""
    if Employee.query.count() > 0:
        return

    employees = [
        Employee(employee_code='NV001', full_name='Nguyễn Văn An',
                 email='an.nguyen@company.vn', phone='0901234567',
                 department='Kỹ thuật', position='Kỹ sư phần mềm'),
        Employee(employee_code='NV002', full_name='Trần Thị Bình',
                 email='binh.tran@company.vn', phone='0912345678',
                 department='Kỹ thuật', position='Lập trình viên'),
        Employee(employee_code='NV003', full_name='Lê Minh Cường',
                 email='cuong.le@company.vn', phone='0923456789',
                 department='Kinh doanh', position='Chuyên viên kinh doanh'),
        Employee(employee_code='NV004', full_name='Phạm Thu Hà',
                 email='ha.pham@company.vn', phone='0934567890',
                 department='Nhân sự', position='Chuyên viên nhân sự'),
        Employee(employee_code='NV005', full_name='Hoàng Đức Dũng',
                 email='dung.hoang@company.vn', phone='0945678901',
                 department='Kế toán', position='Kế toán viên'),
        Employee(employee_code='NV006', full_name='Võ Thị Lan',
                 email='lan.vo@company.vn', phone='0956789012',
                 department='Kinh doanh', position='Trưởng phòng kinh doanh'),
    ]
    db.session.add_all(employees)

    tasks = [
        Task(task_code='CV001', task_name='Phát triển module đăng nhập',
             description='Xây dựng chức năng đăng nhập và phân quyền hệ thống',
             priority='High', duration=4.0),
        Task(task_code='CV002', task_name='Họp khách hàng Q3',
             description='Họp tổng kết quý 3 với khách hàng doanh nghiệp',
             priority='Critical', duration=2.0),
        Task(task_code='CV003', task_name='Kiểm thử hệ thống',
             description='QA và kiểm thử toàn bộ chức năng trước khi ra mắt',
             priority='High', duration=4.0),
        Task(task_code='CV004', task_name='Soạn thảo hợp đồng',
             description='Soạn thảo hợp đồng hợp tác với đối tác mới',
             priority='Medium', duration=2.0),
        Task(task_code='CV005', task_name='Đào tạo nhân viên mới',
             description='Hướng dẫn quy trình làm việc cho nhân viên mới',
             priority='Medium', duration=3.0),
        Task(task_code='CV006', task_name='Lập báo cáo tài chính',
             description='Tổng hợp và lập báo cáo tài chính tháng',
             priority='High', duration=4.0),
        Task(task_code='CV007', task_name='Bảo trì máy chủ',
             description='Cập nhật và bảo trì hệ thống máy chủ định kỳ',
             priority='Low', duration=2.0),
        Task(task_code='CV008', task_name='Thiết kế giao diện người dùng',
             description='Thiết kế UI/UX cho ứng dụng di động mới',
             priority='Medium', duration=4.0),
    ]
    db.session.add_all(tasks)
    db.session.commit()

    # Create sample schedules for current week
    from datetime import date, timedelta
    today = date.today()
    weekday = today.weekday()
    monday = today - timedelta(days=weekday)

    schedule_data = [
        # Monday
        (0, 0, 0, 'morning'),
        (0, 1, 1, 'morning'),
        (0, 2, 2, 'afternoon'),
        (0, 3, 3, 'afternoon'),
        # Tuesday
        (1, 1, 2, 'morning'),
        (1, 4, 5, 'morning'),
        (1, 0, 4, 'afternoon'),
        # Wednesday
        (2, 2, 0, 'morning'),
        (2, 3, 6, 'morning'),
        (2, 5, 7, 'afternoon'),
        # Thursday
        (3, 0, 1, 'morning'),
        (3, 4, 3, 'afternoon'),
        # Friday
        (4, 1, 4, 'morning'),
        (4, 2, 5, 'afternoon'),
        (4, 5, 2, 'afternoon'),
        # Saturday
        (5, 3, 0, 'morning'),
        (5, 0, 6, 'afternoon'),
    ]

    schedules = []
    for day_offset, emp_idx, task_idx, shift in schedule_data:
        work_date = monday + timedelta(days=day_offset)
        # Skip Sunday (shouldn't happen since max offset=5)
        if work_date.weekday() < 6:
            schedules.append(Schedule(
                employee_id=employees[emp_idx].id,
                task_id=tasks[task_idx].id,
                work_date=work_date,
                shift=shift,
            ))

    db.session.add_all(schedules)
    db.session.commit()
    print('Seed data inserted successfully!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
