from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from datetime import datetime, timedelta, date
import csv
import io
from app import db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule

bp = Blueprint('schedule', __name__)

def get_date_from_weekday(weekday_str):
    mapping = {'Thứ 2': 0, 'Thứ 3': 1, 'Thứ 4': 2, 'Thứ 5': 3, 'Thứ 6': 4, 'Thứ 7': 5, 'Chủ Nhật': 6}
    target_weekday = mapping.get(weekday_str, 0)
    today = date.today()
    current_weekday = today.weekday()
    diff = target_weekday - current_weekday
    return today + timedelta(days=diff)

def check_workload_and_expertise(employee_id, task_id, sched_date, is_overtime, exclude_sched_id=None):
    emp = Employee.query.get(employee_id)
    task = Task.query.get(task_id)
    
    # 1. Check Expertise
    if task.required_expertise and task.required_expertise != emp.department:
        flash(f'CẢNH BÁO: Chuyên môn ({task.required_expertise}) không khớp với phòng ban của nhân viên.', 'warning')

    # 2. Check 8-hour limit per day
    workload_query = Schedule.query.filter_by(
        employee_id=employee_id,
        date=sched_date
    )
    if exclude_sched_id:
        workload_query = workload_query.filter(Schedule.id != exclude_sched_id)
        
    existing_schedules = workload_query.all()
    total_hours = sum([s.task.duration for s in existing_schedules if s.task])
    
    if total_hours + task.duration > 8 and not is_overtime:
        return f'LỖI: Nhân viên {emp.fullname} sẽ làm việc {total_hours + task.duration} tiếng trong ngày {sched_date.strftime("%d/%m/%Y")} (Vượt quá 8 tiếng). Hãy check chọn [Tăng ca] để cho phép phân công.'
        
    return None

@bp.route('/')
def index():
    emp_id = request.args.get('employee_id', type=int)
    shift_filter = request.args.get('shift', '')
    
    query = Schedule.query

    if emp_id:
        query = query.filter_by(employee_id=emp_id)
    if shift_filter:
        query = query.filter_by(shift=shift_filter)

    schedules = query.order_by(Schedule.date.desc()).all()
    employees = Employee.query.all()
    tasks = Task.query.all()
    
    return render_template(
        'schedule/index.html',
        schedules=schedules,
        employees=employees,
        tasks=tasks,
        selected_emp=emp_id,
        selected_shift=shift_filter
    )

@bp.route('/add', methods=['POST'])
def add():
    employee_id = request.form.get('employee_id', type=int)
    task_id = request.form.get('task_id', type=int)
    day_of_week = request.form.get('day_of_week')
    shift = request.form.get('shift')
    is_overtime = True if request.form.get('is_overtime') else False

    if not employee_id or not task_id or not day_of_week or not shift:
        flash('Vui lòng điền đầy đủ các thông tin phân công!', 'danger')
        return redirect(url_for('schedule.index'))

    sched_date = get_date_from_weekday(day_of_week)

    error_msg = check_workload_and_expertise(employee_id, task_id, sched_date, is_overtime)
    if error_msg:
        flash(error_msg, 'danger')
        return redirect(url_for('schedule.index'))

    new_sched = Schedule(
        employee_id=employee_id,
        task_id=task_id,
        date=sched_date,
        shift=shift,
        is_overtime=is_overtime
    )
    db.session.add(new_sched)
    db.session.commit()
    flash('Phân công công việc thành công!', 'success')
    return redirect(url_for('schedule.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    sched = Schedule.query.get_or_404(id)
    
    employee_id = request.form.get('employee_id', type=int)
    task_id = request.form.get('task_id', type=int)
    day_of_week = request.form.get('day_of_week')
    shift = request.form.get('shift')
    is_overtime = True if request.form.get('is_overtime') else False

    if not employee_id or not task_id or not day_of_week or not shift:
        flash('Vui lòng điền đầy đủ thông tin!', 'danger')
        return redirect(url_for('schedule.index'))
        
    sched_date = get_date_from_weekday(day_of_week)

    error_msg = check_workload_and_expertise(employee_id, task_id, sched_date, is_overtime, exclude_sched_id=id)
    if error_msg:
        flash(error_msg, 'danger')
        return redirect(url_for('schedule.index'))

    sched.employee_id = employee_id
    sched.task_id = task_id
    sched.date = sched_date
    sched.shift = shift
    sched.is_overtime = is_overtime

    db.session.commit()
    flash('Cập nhật phân công thành công!', 'success')
    return redirect(url_for('schedule.index'))

@bp.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    sched = Schedule.query.get_or_404(id)
    db.session.delete(sched)
    db.session.commit()
    flash('Đã hủy lịch phân công!', 'warning')
    return redirect(url_for('schedule.index'))

@bp.route('/taskboard')
def taskboard():
    schedules = Schedule.query.all()
    todo = [s for s in schedules if s.status == 'Todo']
    in_progress = [s for s in schedules if s.status == 'In Progress']
    done = [s for s in schedules if s.status == 'Done']
    
    return render_template(
        'schedule/taskboard.html',
        todo=todo,
        in_progress=in_progress,
        done=done
    )

@bp.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    sched = Schedule.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status')
    if new_status in ['Todo', 'In Progress', 'Done']:
        sched.status = new_status
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@bp.route('/export')
def export_csv():
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    output = io.StringIO()
    output.write('\ufeff') 
    writer = csv.writer(output)
    writer.writerow(['Mã Lịch', 'Ngày Phân Công', 'Ca Làm Việc', 'Tăng Ca', 'Trạng Thái', 'Mã NV', 'Tên Nhân Viên', 'Phòng Ban', 'Mã CV', 'Tên Công Việc', 'Thời gian (Giờ)', 'Lương Thực Nhận (VNĐ)'])
    for s in schedules:
        salary = s.task.duration * s.employee.base_salary_per_hour
        if s.is_overtime:
            salary *= 2
            
        writer.writerow([
            f'SCH-{s.id}',
            s.date.strftime('%d/%m/%Y'),
            s.shift,
            'Có' if s.is_overtime else 'Không',
            s.status,
            s.employee.code,
            s.employee.fullname,
            s.employee.department,
            s.task.code,
            s.task.task_name,
            s.task.duration,
            salary
        ])
    response = Response(output.getvalue(), mimetype='text/csv')
    # Change filename to .csv but clarify it's Excel compatible
    response.headers['Content-Disposition'] = 'attachment; filename=Bao_Cao_Phan_Cong.csv'
    return response
