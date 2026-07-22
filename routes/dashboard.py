from flask import Blueprint, render_template
from models import db, Employee, Task, Schedule
from datetime import date
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')


@dashboard_bp.route('/')
def index():
    today = date.today()

    total_employees = Employee.query.count()
    total_tasks = Task.query.count()
    total_schedules = Schedule.query.count()

    # Lịch hôm nay
    today_schedules = Schedule.query.filter_by(work_date=today).all()

    # Nhân viên đang làm hôm nay (unique)
    active_employee_ids = db.session.query(Schedule.employee_id).filter_by(
        work_date=today).distinct().all()
    active_employees = Employee.query.filter(
        Employee.id.in_([e[0] for e in active_employee_ids])
    ).all()

    # Thống kê theo bộ phận
    dept_stats = db.session.query(
        Employee.department,
        func.count(Employee.id).label('count')
    ).group_by(Employee.department).all()

    # Thống kê lịch 7 ngày gần đây
    from datetime import timedelta
    recent_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    schedule_counts = []
    for d in recent_dates:
        cnt = Schedule.query.filter_by(work_date=d).count()
        schedule_counts.append({'date': d.strftime('%d/%m'), 'count': cnt})

    return render_template('dashboard.html',
                           total_employees=total_employees,
                           total_tasks=total_tasks,
                           total_schedules=total_schedules,
                           today_schedules=today_schedules,
                           active_employees=active_employees,
                           dept_stats=dept_stats,
                           schedule_counts=schedule_counts,
                           today=today)
