from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Schedule, Employee, Task
from datetime import date, timedelta, datetime

schedules_bp = Blueprint('schedules', __name__, url_prefix='/schedules')

SHIFT_LABELS = {
    'morning': 'Ca Sáng (07:30–11:30)',
    'afternoon': 'Ca Chiều (13:00–17:00)'
}

WEEKDAY_VI = {0: 'Thứ Hai', 1: 'Thứ Ba', 2: 'Thứ Tư',
              3: 'Thứ Năm', 4: 'Thứ Sáu', 5: 'Thứ Bảy'}


def get_week_dates(ref_date=None):
    """Trả về danh sách ngày T2→T6 trong tuần chứa ref_date."""
    if ref_date is None:
        ref_date = date.today()
    # Thứ Hai = weekday() == 0
    monday = ref_date - timedelta(days=ref_date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]  # T2 → T7


@schedules_bp.route('/')
def index():
    search = request.args.get('search', '').strip()
    query = Schedule.query.join(Employee).join(Task)

    if search:
        query = query.filter(
            db.or_(
                Employee.full_name.ilike(f'%{search}%'),
                Task.task_name.ilike(f'%{search}%'),
            )
        )

    schedules = query.order_by(Schedule.work_date.desc(), Schedule.shift).all()
    return render_template('schedules/list.html',
                           schedules=schedules,
                           search=search,
                           shift_labels=SHIFT_LABELS)


@schedules_bp.route('/add', methods=['GET', 'POST'])
def add():
    employees = Employee.query.order_by(Employee.full_name).all()
    tasks = Task.query.order_by(Task.task_name).all()

    if request.method == 'POST':
        employee_id = request.form.get('employee_id', type=int)
        task_id = request.form.get('task_id', type=int)
        work_date_str = request.form.get('work_date', '').strip()
        shift = request.form.get('shift', '').strip()

        # Parse date
        try:
            work_date = datetime.strptime(work_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Ngày làm việc không hợp lệ!', 'danger')
            return render_template('schedules/form.html',
                                   employees=employees, tasks=tasks,
                                   shift_labels=SHIFT_LABELS)

        # Chỉ cho T2→T7
        if work_date.weekday() == 6:  # Chủ nhật
            flash('Hệ thống chỉ hoạt động từ Thứ Hai đến Thứ Bảy!', 'danger')
            return render_template('schedules/form.html',
                                   employees=employees, tasks=tasks,
                                   shift_labels=SHIFT_LABELS)

        # Kiểm tra trùng ca
        conflict = Schedule.query.filter_by(
            employee_id=employee_id,
            work_date=work_date,
            shift=shift
        ).first()

        if conflict:
            emp = Employee.query.get(employee_id)
            flash(
                f'❌ Nhân viên <strong>{emp.full_name}</strong> đã được phân công '
                f'<strong>{SHIFT_LABELS.get(shift, shift)}</strong> '
                f'ngày <strong>{work_date.strftime("%d/%m/%Y")}</strong>! '
                f'Vui lòng chọn ca khác.',
                'danger'
            )
            return render_template('schedules/form.html',
                                   employees=employees, tasks=tasks,
                                   shift_labels=SHIFT_LABELS,
                                   form_data=request.form)

        schedule = Schedule(
            employee_id=employee_id,
            task_id=task_id,
            work_date=work_date,
            shift=shift
        )
        db.session.add(schedule)
        db.session.commit()
        flash('✅ Phân công công việc thành công!', 'success')
        return redirect(url_for('schedules.index'))

    return render_template('schedules/form.html',
                           employees=employees, tasks=tasks,
                           shift_labels=SHIFT_LABELS, form_data=None)


@schedules_bp.route('/delete/<int:sched_id>', methods=['POST'])
def delete(sched_id):
    sched = Schedule.query.get_or_404(sched_id)
    db.session.delete(sched)
    db.session.commit()
    flash('Đã hủy phân công!', 'warning')
    return redirect(url_for('schedules.index'))


@schedules_bp.route('/calendar')
def calendar():
    week_str = request.args.get('week', '')
    try:
        ref_date = datetime.strptime(week_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        ref_date = date.today()

    week_dates = get_week_dates(ref_date)
    prev_week = (week_dates[0] - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (week_dates[0] + timedelta(days=7)).strftime('%Y-%m-%d')

    # Lấy tất cả lịch trong tuần
    schedules = Schedule.query.filter(
        Schedule.work_date >= week_dates[0],
        Schedule.work_date <= week_dates[-1]
    ).all()

    # Tổ chức: calendar_data[date][shift] = list of schedules
    calendar_data = {}
    for d in week_dates:
        calendar_data[d] = {'morning': [], 'afternoon': []}
    for s in schedules:
        if s.work_date in calendar_data:
            calendar_data[s.work_date][s.shift].append(s)

    return render_template('schedules/calendar.html',
                           week_dates=week_dates,
                           calendar_data=calendar_data,
                           weekday_vi=WEEKDAY_VI,
                           prev_week=prev_week,
                           next_week=next_week,
                           today=date.today())
