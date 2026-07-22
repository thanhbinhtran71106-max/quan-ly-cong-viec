from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Employee

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')


@employees_bp.route('/')
def index():
    search = request.args.get('search', '').strip()
    dept = request.args.get('department', '').strip()

    query = Employee.query
    if search:
        query = query.filter(
            db.or_(
                Employee.full_name.ilike(f'%{search}%'),
                Employee.employee_code.ilike(f'%{search}%'),
                Employee.email.ilike(f'%{search}%'),
            )
        )
    if dept:
        query = query.filter(Employee.department == dept)

    employees = query.order_by(Employee.created_at.desc()).all()
    departments = db.session.query(Employee.department).distinct().all()
    departments = [d[0] for d in departments]

    return render_template('employees/list.html',
                           employees=employees,
                           departments=departments,
                           search=search,
                           selected_dept=dept)


@employees_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        employee_code = request.form.get('employee_code', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        position = request.form.get('position', '').strip()

        # Validate trùng mã/email
        if Employee.query.filter_by(employee_code=employee_code).first():
            flash('Mã nhân viên đã tồn tại!', 'danger')
            return redirect(url_for('employees.add'))
        if Employee.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('employees.add'))

        emp = Employee(
            employee_code=employee_code,
            full_name=full_name,
            email=email,
            phone=phone,
            department=department,
            position=position
        )
        db.session.add(emp)
        db.session.commit()
        flash(f'Đã thêm nhân viên {full_name} thành công!', 'success')
        return redirect(url_for('employees.index'))

    return render_template('employees/form.html', employee=None, action='add')


@employees_bp.route('/edit/<int:emp_id>', methods=['GET', 'POST'])
def edit(emp_id):
    emp = Employee.query.get_or_404(emp_id)

    if request.method == 'POST':
        employee_code = request.form.get('employee_code', '').strip()
        email = request.form.get('email', '').strip()

        # Kiểm tra trùng mã với nhân viên khác
        dup_code = Employee.query.filter(
            Employee.employee_code == employee_code,
            Employee.id != emp_id
        ).first()
        if dup_code:
            flash('Mã nhân viên đã tồn tại!', 'danger')
            return redirect(url_for('employees.edit', emp_id=emp_id))

        dup_email = Employee.query.filter(
            Employee.email == email,
            Employee.id != emp_id
        ).first()
        if dup_email:
            flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('employees.edit', emp_id=emp_id))

        emp.employee_code = employee_code
        emp.full_name = request.form.get('full_name', '').strip()
        emp.email = email
        emp.phone = request.form.get('phone', '').strip()
        emp.department = request.form.get('department', '').strip()
        emp.position = request.form.get('position', '').strip()

        db.session.commit()
        flash(f'Đã cập nhật nhân viên {emp.full_name} thành công!', 'success')
        return redirect(url_for('employees.index'))

    return render_template('employees/form.html', employee=emp, action='edit')


@employees_bp.route('/delete/<int:emp_id>', methods=['POST'])
def delete(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    name = emp.full_name
    db.session.delete(emp)
    db.session.commit()
    flash(f'Đã xóa nhân viên {name}!', 'warning')
    return redirect(url_for('employees.index'))


@employees_bp.route('/api/list')
def api_list():
    employees = Employee.query.order_by(Employee.full_name).all()
    return jsonify([e.to_dict() for e in employees])
