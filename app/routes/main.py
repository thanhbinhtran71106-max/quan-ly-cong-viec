from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date, datetime, timedelta
from app.models import Employee, Task, Schedule
from app import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    today = date.today()
    
    # Handle Quick Assign POST
    if request.method == 'POST':
        emp_id = request.form.get('employee_id', type=int)
        task_id = request.form.get('task_id', type=int)
        work_date_str = request.form.get('work_date', '').strip()
        shift = request.form.get('shift', '').strip()
        
        try:
            work_date = datetime.strptime(work_date_str, '%Y-%m-%d').date()
            if work_date.weekday() > 5:
                flash('Chỉ được phân công từ Thứ Hai đến Thứ Bảy.', 'danger')
            else:
                existing = Schedule.query.filter_by(employee_id=emp_id, work_date=work_date, shift=shift).first()
                if existing:
                    flash('Nhân viên đã có lịch trong ca này!', 'danger')
                else:
                    schedule = Schedule(employee_id=emp_id, task_id=task_id, work_date=work_date, shift=shift)
                    db.session.add(schedule)
                    db.session.commit()
                    flash('Phân công thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
    
    total_employees = Employee.query.count()
    total_tasks = Task.query.count()
    total_schedules = Schedule.query.count()

    today_schedules = Schedule.query.filter_by(work_date=today).all()
    today_employees = len(list({s.employee for s in today_schedules}))

    # Data for quick assign
    employees = Employee.query.order_by(Employee.full_name).all()
    tasks = Task.query.order_by(Task.task_name).all()

    # Data for weekly grid
    from app.routes.schedules import get_week_range
    monday, saturday = get_week_range(today)
    work_dates = [monday + timedelta(days=i) for i in range(6)]
    
    weekly_schedules = Schedule.query.filter(
        Schedule.work_date >= monday,
        Schedule.work_date <= saturday
    ).all()
    
    # grid[emp_id] = { 'employee': emp, 'dates': { date: {'morning': task, 'afternoon': task} } }
    weekly_grid = {}
    for emp in employees:
        weekly_grid[emp.id] = {
            'employee': emp,
            'dates': {d: {'morning': None, 'afternoon': None} for d in work_dates}
        }
    
    for s in weekly_schedules:
        if s.employee_id in weekly_grid and s.work_date in weekly_grid[s.employee_id]['dates']:
            weekly_grid[s.employee_id]['dates'][s.work_date][s.shift] = s

    return render_template('dashboard.html',
                           total_employees=total_employees,
                           total_tasks=total_tasks,
                           total_schedules=total_schedules,
                           today_schedules=today_schedules,
                           today_employees=today_employees,
                           employees=employees,
                           tasks=tasks,
                           weekly_grid=weekly_grid.values(),
                           work_dates=work_dates,
                           today=today,
                           monday=monday,
                           saturday=saturday)
