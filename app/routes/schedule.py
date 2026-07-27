from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from datetime import datetime, timedelta
import csv
import io
from app import db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule

bp = Blueprint('schedule', __name__)

def check_workload_and_expertise(employee_id, task_id, sched_date, shift, exclude_sched_id=None, allow_overtime=False):
    emp = Employee.query.get(employee_id)
    task = Task.query.get(task_id)
    
    # 1. Check Expertise
    if task.required_expertise and task.required_expertise != emp.department:
        flash(f'CẢNH BÁO: Chuyên môn yêu cầu của công việc ({task.required_expertise}) không khớp với phòng ban của nhân viên ({emp.department}).', 'warning')

    # 2. Check Workload (>= 2 tasks in the same shift)
    if not allow_overtime:
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
            return f'LỖI: Không thể đăng ký thêm! Nhân viên {emp.fullname} đã bị quá tải (>= 2 công việc) trong ca {shift} ngày {sched_date.strftime("%d/%m/%Y")}.{suggest_msg}'
        
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
    employee_id_input = request.form.get('employee_id')
    task_id = request.form.get('task_id', type=int)
    weekday = request.form.get('weekday', type=int)
    shift = request.form.get('shift')
    allow_overtime = request.form.get('overtime') == 'on'

    if not task_id or weekday is None or not shift:
        flash('Vui lòng điền đầy đủ các thông tin phân công!', 'danger')
        return redirect(url_for('schedule.index'))

    # Tự động quy đổi Thứ trong tuần sang Ngày (Date)
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    sched_date = start_of_week + timedelta(days=weekday)
    
    task = Task.query.get_or_404(task_id)

    # Xử lý tự động phân công hàng loạt
    if not employee_id_input:
        flash('LỖI: Chưa có nhân viên nào được bốc tự động.', 'danger')
        return redirect(url_for('schedule.index'))

    emp_ids = [int(x) for x in employee_id_input.split(',')]
    assigned_count = 0
    
    for emp_id in emp_ids:
        error_msg = check_workload_and_expertise(emp_id, task_id, sched_date, shift, allow_overtime=allow_overtime)
        if error_msg:
            flash(error_msg, 'warning')
            continue

        new_sched = Schedule(
            employee_id=emp_id,
            task_id=task_id,
            date=sched_date,
            shift=shift
        )
        db.session.add(new_sched)
        assigned_count += 1
        
    db.session.commit()
    
    if assigned_count > 0:
        flash(f'Phân công công việc thành công cho {assigned_count} nhân viên!', 'success')
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

@bp.route('/weekly')
def weekly():
    emp_id = request.args.get('employee_id', type=int)
    
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=5) # Mon to Sat
    
    query = Schedule.query.filter(Schedule.date >= start_of_week, Schedule.date <= end_of_week)
    if emp_id:
        query = query.filter_by(employee_id=emp_id)
        
    schedules = query.all()
    employees = Employee.query.all()
    emp_list = [e for e in employees if e.id == emp_id] if emp_id else employees
    
    # Group schedules by employee, then by day of week (0-5)
    weekly_data = {}
    for emp in emp_list:
        weekly_data[emp] = {}
        for day in range(6):
            weekly_data[emp][day] = {'Sáng': [], 'Chiều': []}
            
    for sched in schedules:
        day_index = sched.date.weekday()
        if day_index < 6 and sched.employee in weekly_data:
            weekly_data[sched.employee][day_index][sched.shift].append(sched)
            
    # Dates for the header
    week_dates = [(start_of_week + timedelta(days=i)).strftime('%d/%m') for i in range(6)]
            
    return render_template(
        'schedule/weekly.html',
        weekly_data=weekly_data,
        week_dates=week_dates,
        start_date=start_of_week.strftime('%d/%m/%Y'),
        end_date=end_of_week.strftime('%d/%m/%Y'),
        employees=employees,
        selected_emp=emp_id
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
    output.write('sep=,\n')
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

@bp.route('/api/suggest-employee', methods=['GET'])
def suggest_employee():
    task_id = request.args.get('task_id', type=int)
    weekday = request.args.get('weekday', type=int)
    shift = request.args.get('shift')
    allow_overtime = request.args.get('overtime') == 'true'

    if not task_id or weekday is None or not shift:
        return jsonify({'success': False, 'message': 'Thiếu tham số'})

    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    sched_date = start_of_week + timedelta(days=weekday)
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Không tìm thấy công việc'})

    candidates = Employee.query.filter_by(department=task.required_expertise).all() if task.required_expertise else Employee.query.all()
    
    free_employees = []
    for emp in candidates:
        workload = Schedule.query.filter_by(employee_id=emp.id, date=sched_date, shift=shift).count()
        limit = 999 if allow_overtime else 2
        if workload < limit:
            free_employees.append({
                'id': emp.id,
                'fullname': emp.fullname,
                'department': emp.department
            })
            
    if free_employees:
        return jsonify({
            'success': True, 
            'employees': free_employees
        })
            
    return jsonify({
        'success': False, 
        'message': f'Không thể đăng ký thêm! Tất cả nhân viên đều đã quá tải trong ca {shift} ngày {sched_date.strftime("%d/%m/%Y")}.'
    })

@bp.route('/auto-generate', methods=['POST'])
def auto_generate():
    import random
    
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    employees = Employee.query.all()
    tasks = Task.query.all()
    
    if not tasks or not employees:
        flash('Cần có ít nhất 1 nhân viên và 1 công việc để phân công tự động!', 'danger')
        return redirect(url_for('schedule.index'))

    assigned_count = 0
    for emp in employees:
        # Danh sách việc đúng chuyên môn
        dept_tasks = [t for t in tasks if t.required_expertise == emp.department]
        if not dept_tasks:
            continue
            
        for day in range(6): # Thứ 2 tới Thứ 7 (0-5)
            sched_date = start_of_week + timedelta(days=day)
            
            for shift in ['Sáng', 'Chiều']:
                # Kiểm tra lịch đã tồn tại
                existing = Schedule.query.filter_by(employee_id=emp.id, date=sched_date, shift=shift).first()
                if existing:
                    continue
                    
                # 60% xác suất được phân công (để tạo khoảng trống thực tế)
                if random.random() > 0.4:
                    new_sched = Schedule(
                        employee_id=emp.id,
                        task_id=random.choice(dept_tasks).id,
                        date=sched_date,
                        shift=shift,
                        status='Todo'
                    )
                    db.session.add(new_sched)
                    assigned_count += 1

    db.session.commit()
    flash(f'✨ Tự động phân công hoàn tất! Đã xếp {assigned_count} lịch làm việc mới cho tuần này.', 'success')
    return redirect(url_for('schedule.weekly'))

