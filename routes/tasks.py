from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Task

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

PRIORITY_LABELS = {'low': 'Thấp', 'medium': 'Trung bình', 'high': 'Cao'}


@tasks_bp.route('/')
def index():
    search = request.args.get('search', '').strip()
    priority = request.args.get('priority', '').strip()

    query = Task.query
    if search:
        query = query.filter(
            db.or_(
                Task.task_name.ilike(f'%{search}%'),
                Task.task_code.ilike(f'%{search}%'),
            )
        )
    if priority:
        query = query.filter(Task.priority == priority)

    tasks = query.order_by(Task.created_at.desc()).all()
    return render_template('tasks/list.html',
                           tasks=tasks,
                           search=search,
                           selected_priority=priority,
                           priority_labels=PRIORITY_LABELS)


@tasks_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        task_code = request.form.get('task_code', '').strip()
        task_name = request.form.get('task_name', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        duration = request.form.get('duration', '').strip()

        if Task.query.filter_by(task_code=task_code).first():
            flash('Mã công việc đã tồn tại!', 'danger')
            return redirect(url_for('tasks.add'))

        task = Task(
            task_code=task_code,
            task_name=task_name,
            description=description,
            priority=priority,
            duration=duration
        )
        db.session.add(task)
        db.session.commit()
        flash(f'Đã thêm công việc "{task_name}" thành công!', 'success')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/form.html', task=None, action='add',
                           priority_labels=PRIORITY_LABELS)


@tasks_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        task_code = request.form.get('task_code', '').strip()
        dup = Task.query.filter(
            Task.task_code == task_code,
            Task.id != task_id
        ).first()
        if dup:
            flash('Mã công việc đã tồn tại!', 'danger')
            return redirect(url_for('tasks.edit', task_id=task_id))

        task.task_code = task_code
        task.task_name = request.form.get('task_name', '').strip()
        task.description = request.form.get('description', '').strip()
        task.priority = request.form.get('priority', 'medium')
        task.duration = request.form.get('duration', '').strip()

        db.session.commit()
        flash(f'Đã cập nhật công việc "{task.task_name}" thành công!', 'success')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/form.html', task=task, action='edit',
                           priority_labels=PRIORITY_LABELS)


@tasks_bp.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    name = task.task_name
    db.session.delete(task)
    db.session.commit()
    flash(f'Đã xóa công việc "{name}"!', 'warning')
    return redirect(url_for('tasks.index'))


@tasks_bp.route('/api/list')
def api_list():
    tasks = Task.query.order_by(Task.task_name).all()
    return jsonify([t.to_dict() for t in tasks])
