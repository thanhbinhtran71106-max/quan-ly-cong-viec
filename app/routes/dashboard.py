from flask import Blueprint, render_template, request
import json
from datetime import datetime, date
from app import db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule

bp = Blueprint('dashboard', __name__)

def seed_sample_data():
    if Employee.query.count() == 0:
        emp1 = Employee(code='NV001', fullname='Nguyễn Văn An', email='an.nguyen@company.com', phone='0901112223', department='Kỹ thuật', position='Kỹ sư trưởng')
        emp2 = Employee(code='NV002', fullname='Trần Thị Bình', email='binh.tran@company.com', phone='0902223334', department='Kinh doanh', position='Trưởng phòng KD')
        emp3 = Employee(code='NV003', fullname='Lê Văn Cường', email='cuong.le@company.com', phone='0903334445', department='Kế toán', position='Kế toán viên')
        emp4 = Employee(code='NV004', fullname='Phạm Thị Dung', email='dung.pham@company.com', phone='0904445556', department='Hành chính', position='Chuyên viên HR')
        emp5 = Employee(code='NV005', fullname='Hoàng Văn Em', email='em.hoang@company.com', phone='0905556667', department='IT Support', position='Quản trị mạng')
        db.session.add_all([emp1, emp2, emp3, emp4, emp5])
        db.session.commit()

    if Task.query.count() == 0:
        t1 = Task(code='CV001', task_name='Bảo trì máy chủ & Server', priority='Cao', duration=4, description='Kiểm tra hệ thống Server định kỳ')
        t2 = Task(code='CV002', task_name='Tư vấn KH & Chăm sóc Lead', priority='Trung bình', duration=4, description='Gọi điện tư vấn khách hàng doanh nghiệp')
        t3 = Task(code='CV003', task_name='Lập hóa đơn & Đối chiếu công nợ', priority='Thường', duration=4, description='Xuất hóa đơn GTGT và kiểm tra chứng từ')
        t4 = Task(code='CV004', task_name='Đăng tin tuyển dụng & Phỏng vấn', priority='Trung bình', duration=4, description='Sàng lọc hồ sơ ứng viên vị trí mới')
        db.session.add_all([t1, t2, t3, t4])
        db.session.commit()

@bp.route('/')
@bp.route('/dashboard')
def index():
    seed_sample_data()

    total_employees = Employee.query.count()
    total_tasks = Task.query.count()
    total_schedules = Schedule.query.count()
    
    # Active today
    today = date.today()
    schedules_today = Schedule.query.filter_by(date=today).all()
    active_today = len(schedules_today)
    morning_active = len([s for s in schedules_today if s.shift == 'Sáng'])
    afternoon_active = len([s for s in schedules_today if s.shift == 'Chiều'])

    stats = {
        'total_employees': total_employees,
        'employees_trend': '+3 so với tuần trước',
        'total_tasks': total_tasks,
        'tasks_trend': 'Danh mục đầy đủ',
        'total_schedules': total_schedules,
        'schedules_trend': 'Tự động kiểm tra trùng',
        'active_today': active_today,
        'morning_active': morning_active,
        'afternoon_active': afternoon_active
    }

    employees = Employee.query.all()
    tasks = Task.query.all()

    # Pre-built Matrix Schedule mockup days for Monday to Saturday
    days = [
        {'name': 'Thứ 2', 'date': '19/05', 'is_today': True},
        {'name': 'Thứ 3', 'date': '20/05', 'is_today': False},
        {'name': 'Thứ 4', 'date': '21/05', 'is_today': False},
        {'name': 'Thứ 5', 'date': '22/05', 'is_today': False},
        {'name': 'Thứ 6', 'date': '23/05', 'is_today': False},
        {'name': 'Thứ 7', 'date': '24/05', 'is_today': False},
    ]

    # Tính toán Chart Data
    chart_labels = []
    chart_normal = []
    chart_overtime = []

    for emp in employees:
        chart_labels.append(emp.fullname)
        normal = 0
        overtime = 0
        for s in emp.schedules:
            if s.task:
                if s.is_overtime:
                    overtime += s.task.duration
                else:
                    normal += s.task.duration
        chart_normal.append(normal)
        chart_overtime.append(overtime)

    chart_data = json.dumps({
        'labels': chart_labels,
        'normal_hours': chart_normal,
        'overtime_hours': chart_overtime
    })

    return render_template(
        'dashboard/index.html',
        stats=stats,
        employees=employees,
        tasks=tasks,
        days=days,
        chart_data=chart_data
    )
