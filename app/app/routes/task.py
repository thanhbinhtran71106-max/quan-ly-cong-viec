from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app import db
from app.models.task import Task

bp = Blueprint('task', __name__)

@bp.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        tasks = Task.query.filter(
            (Task.task_name.like(f'%{search_query}%')) |
            (Task.code.like(f'%{search_query}%')) |
            (Task.priority.like(f'%{search_query}%'))
        ).all()
    else:
        tasks = Task.query.all()
    return render_template('task/index.html', tasks=tasks, search_query=search_query)

@bp.route('/add', methods=['POST'])
def add():
    code = request.form.get('code')
    task_name = request.form.get('task_name')
    priority = request.form.get('priority')
    duration = request.form.get('duration', type=int)
    description = request.form.get('description')
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    required_expertise = request.form.get('required_expertise')

    if not code or not task_name:
        flash('Vui lòng nhập đầy đủ thông tin công việc!', 'danger')
        return redirect(url_for('task.index'))

    existing = Task.query.filter_by(code=code).first()
    if existing:
        flash(f'Mã công việc {code} đã tồn tại!', 'danger')
        return redirect(url_for('task.index'))

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

    new_task = Task(
        code=code,
        task_name=task_name,
        priority=priority,
        duration=duration or 4,
        description=description,
        start_date=start_date,
        end_date=end_date,
        required_expertise=required_expertise
    )
    db.session.add(new_task)
    db.session.commit()
    flash('Thêm công việc mới thành công!', 'success')
    return redirect(url_for('task.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    task_obj = Task.query.get_or_404(id)
    task_obj.task_name = request.form.get('task_name')
    task_obj.priority = request.form.get('priority')
    task_obj.duration = request.form.get('duration', type=int)
    task_obj.description = request.form.get('description')
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    task_obj.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    task_obj.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    task_obj.required_expertise = request.form.get('required_expertise')

    db.session.commit()
    flash('Cập nhật công việc thành công!', 'success')
    return redirect(url_for('task.index'))

@bp.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    task_obj = Task.query.get_or_404(id)
    db.session.delete(task_obj)
    db.session.commit()
    flash('Đã xóa công việc khỏi hệ thống!', 'warning')
    return redirect(url_for('task.index'))
