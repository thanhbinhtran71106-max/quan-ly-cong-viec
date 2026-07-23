from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.employee import Employee

bp = Blueprint('employee', __name__)

@bp.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        employees = Employee.query.filter(
            (Employee.fullname.like(f'%{search_query}%')) |
            (Employee.code.like(f'%{search_query}%')) |
            (Employee.department.like(f'%{search_query}%'))
        ).all()
    else:
        employees = Employee.query.all()
    return render_template('employee/index.html', employees=employees, search_query=search_query)

@bp.route('/add', methods=['POST'])
def add():
    code = request.form.get('code')
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    department = request.form.get('department')
    position = request.form.get('position')
    base_salary_per_hour = request.form.get('base_salary_per_hour', type=int, default=50000)

    if not code or not fullname:
        flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
        return redirect(url_for('employee.index'))

    # Check duplicate code
    existing = Employee.query.filter_by(code=code).first()
    if existing:
        flash(f'Mã nhân viên {code} đã tồn tại!', 'danger')
        return redirect(url_for('employee.index'))

    new_emp = Employee(
        code=code,
        fullname=fullname,
        email=email,
        phone=phone,
        department=department,
        position=position,
        base_salary_per_hour=base_salary_per_hour
    )
    db.session.add(new_emp)
    db.session.commit()
    flash('Thêm nhân viên thành công!', 'success')
    return redirect(url_for('employee.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    emp = Employee.query.get_or_404(id)
    emp.fullname = request.form.get('fullname')
    emp.email = request.form.get('email')
    emp.phone = request.form.get('phone')
    emp.department = request.form.get('department')
    emp.position = request.form.get('position')
    emp.base_salary_per_hour = request.form.get('base_salary_per_hour', type=int, default=50000)

    db.session.commit()
    flash('Cập nhật thông tin nhân viên thành công!', 'success')
    return redirect(url_for('employee.index'))

@bp.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash('Đã xóa nhân viên khỏi hệ thống!', 'warning')
    return redirect(url_for('employee.index'))

@bp.route('/propose/<int:id>', methods=['POST'])
def propose(id):
    emp = Employee.query.get_or_404(id)
    proposal = request.form.get('promotion_proposal')
    
    emp.promotion_proposal = proposal
    db.session.commit()
    flash(f'Đã lưu đề xuất thăng tiến cho nhân viên {emp.fullname}!', 'success')
    return redirect(url_for('employee.index'))
