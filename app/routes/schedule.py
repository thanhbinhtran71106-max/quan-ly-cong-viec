from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from datetime import datetime
import csv
import io
from app import db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule

bp = Blueprint('schedule', __name__)

def check_workload_and_expertise(employee_id, task_id, sched_date, shift, exclude_sched_id=None):
    emp = Employee.query.get(employee_id)
    task = Task.query.get(task_id)
    
    # 1. Check Expertise
    if task.required_expertise and task.required_expertise != emp.department:
        flash(f'CẢNH BÁO: Chuyên môn yêu cầu của công việc ({task.required_expertise}) không khớp với phòng ban của nhân viên ({emp.department}).', 'warning')

    # 2. Check Workload (>= 2 tasks in the same shift)
    workload_query = Schedule.query.filter_by(
        employee_id=employee_id,
        date=sched_date,
        shift=shift
    )
    if exclude_sched_id:
        workload_query = workload_query.filter(Schedule.id != exclude_sched_id)
        
    current_tasks_count = workload_query.count()
    
    if current_tasks_count >= 2:
        # Suggest others
        suggested = Employee.query.filter(
            Employee.id != employee_id,
            Employee.department == (task.required_expertise or emp.department)
        ).all()
        suggested_names = ", ".join([e.fullname for e in suggested])
        suggest_msg = f" Gợi ý nhân viên khác: {suggested_names}" if suggested else " Không có nhân viên cùng chuyên môn khác."
        return f'LỖI: Nhân viên {emp.fullname} đã bị quá tải (>= 2 công việc) trong ca {shift} ngày {sched_date.strftime("%d/%m/%Y")}.{suggest_msg}'
        
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
    date_str = request.form.get('date')
    shift = request.form.get('shift')

    if not employee_id or not task_id or not date_str or not shift:
        flash('Vui lòng điền đầy đủ các thông tin phân công!', 'danger')
        return redirect(url_for('schedule.index'))

    sched_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    error_msg = check_workload_and_expertise(employee_id, task_id, sched_date, shift)
    if error_msg:
        flash(error_msg, 'danger')
        return redirect(url_for('schedule.index'))

    new_sched = Schedule(
        employee_id=employee_id,
        task_id=task_id,
        date=sched_date,
        shift=shift
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
    date_str = request.form.get('date')
    shift = request.form.get('shift')

    if not employee_id or not task_id or not date_str or not shift:
        flash('Vui lòng điền đầy đủ thông tin!', 'danger')
        return redirect(url_for('schedule.index'))
        
    sched_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    error_msg = check_workload_and_expertise(employee_id, task_id, sched_date, shift, exclude_sched_id=id)
    if error_msg:
        flash(error_msg, 'danger')
        return redirect(url_for('schedule.index'))

    sched.employee_id = employee_id
    sched.task_id = task_id
    sched.date = sched_date
    sched.shift = shift

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
    writer.writerow(['Mã Lịch', 'Ngày Phân Công', 'Ca Làm Việc', 'Trạng Thái', 'Mã NV', 'Tên Nhân Viên', 'Bộ Phận', 'Mã CV', 'Tên Công Việc', 'Độ Ưu Tiên'])
    for s in schedules:
        writer.writerow([
            f'SCH-{s.id}',
            s.date.strftime('%d/%m/%Y'),
            s.shift,
            s.status,
            s.employee.code,
            s.employee.fullname,
            s.employee.department,
            s.task.code,
            s.task.task_name,
            s.task.priority
        ])
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=Lich_Phan_Cong_Worksheet.csv'
    return response
