from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Task
from app import db
from sqlalchemy.exc import IntegrityError

tasks_bp = Blueprint('tasks', __name__)

PRIORITY_ORDER = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}


@tasks_bp.route('/')
def list_tasks():
    search = request.args.get('search', '').strip()
    priority = request.args.get('priority', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Task.query
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Task.task_name.ilike(like),
                Task.task_code.ilike(like),
                Task.description.ilike(like),
            )
        )
    if priority:
        query = query.filter(Task.priority == priority)

    tasks = query.order_by(Task.task_code).paginate(page=page, per_page=10)
    return render_template('tasks/list.html',
                           tasks=tasks,
                           search=search,
                           selected_priority=priority,
                           priorities=Task.PRIORITY_CHOICES)


@tasks_bp.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        try:
            task = Task(
                task_code=request.form['task_code'].strip().upper(),
                task_name=request.form['task_name'].strip(),
                description=request.form.get('description', '').strip(),
                priority=request.form['priority'],
                duration=float(request.form['duration']),
            )
            db.session.add(task)
            db.session.commit()
            flash(f'Đã thêm công việc "{task.task_name}" thành công!', 'success')
            return redirect(url_for('tasks.list_tasks'))
        except IntegrityError:
            db.session.rollback()
            flash('Mã công việc đã tồn tại!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')

    return render_template('tasks/form.html', task=None, action='add')


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        try:
            task.task_code = request.form['task_code'].strip().upper()
            task.task_name = request.form['task_name'].strip()
            task.description = request.form.get('description', '').strip()
            task.priority = request.form['priority']
            task.duration = float(request.form['duration'])
            db.session.commit()
            flash(f'Đã cập nhật công việc "{task.task_name}"!', 'success')
            return redirect(url_for('tasks.list_tasks'))
        except IntegrityError:
            db.session.rollback()
            flash('Mã công việc đã tồn tại!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')

    return render_template('tasks/form.html', task=task, action='edit')


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        name = task.task_name
        db.session.delete(task)
        db.session.commit()
        flash(f'Đã xóa công việc "{name}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Không thể xóa: {str(e)}', 'danger')
    return redirect(url_for('tasks.list_tasks'))
