from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Employee
from app import db
from sqlalchemy.exc import IntegrityError

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/')
def list_employees():
    search = request.args.get('search', '').strip()
    dept = request.args.get('department', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Employee.query
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Employee.full_name.ilike(like),
                Employee.employee_code.ilike(like),
                Employee.email.ilike(like),
                Employee.phone.ilike(like),
            )
        )
    if dept:
        query = query.filter(Employee.department == dept)

    employees = query.order_by(Employee.employee_code).paginate(page=page, per_page=10)
    departments = db.session.query(Employee.department).distinct().order_by(Employee.department).all()
    departments = [d[0] for d in departments]

    return render_template('employees/list.html',
                           employees=employees,
                           search=search,
                           selected_dept=dept,
                           departments=departments)


@employees_bp.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        try:
            emp = Employee(
                employee_code=request.form['employee_code'].strip().upper(),
                full_name=request.form['full_name'].strip(),
                email=request.form['email'].strip(),
                phone=request.form['phone'].strip(),
                department=request.form['department'].strip(),
                position=request.form['position'].strip(),
            )
            db.session.add(emp)
            db.session.commit()
            flash(f'Đã thêm nhân viên {emp.full_name} thành công!', 'success')
            return redirect(url_for('employees.list_employees'))
        except IntegrityError:
            db.session.rollback()
            flash('Mã nhân viên hoặc email đã tồn tại!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')

    return render_template('employees/form.html', employee=None, action='add')


@employees_bp.route('/<int:emp_id>/edit', methods=['GET', 'POST'])
def edit_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)

    if request.method == 'POST':
        try:
            emp.employee_code = request.form['employee_code'].strip().upper()
            emp.full_name = request.form['full_name'].strip()
            emp.email = request.form['email'].strip()
            emp.phone = request.form['phone'].strip()
            emp.department = request.form['department'].strip()
            emp.position = request.form['position'].strip()
            db.session.commit()
            flash(f'Đã cập nhật nhân viên {emp.full_name}!', 'success')
            return redirect(url_for('employees.list_employees'))
        except IntegrityError:
            db.session.rollback()
            flash('Mã nhân viên hoặc email đã tồn tại!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')

    return render_template('employees/form.html', employee=emp, action='edit')


@employees_bp.route('/<int:emp_id>/delete', methods=['POST'])
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    try:
        name = emp.full_name
        db.session.delete(emp)
        db.session.commit()
        flash(f'Đã xóa nhân viên {name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Không thể xóa: {str(e)}', 'danger')
    return redirect(url_for('employees.list_employees'))


@employees_bp.route('/<int:emp_id>')
def detail_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    from app.models import Schedule
    schedules = Schedule.query.filter_by(employee_id=emp_id).order_by(
        Schedule.work_date.desc()).limit(20).all()
    return render_template('employees/detail.html', employee=emp, schedules=schedules)
