from flask import Blueprint, render_template, request, redirect, url_for, flash, session

bp = Blueprint('auth', __name__)

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        admin_name = request.form.get('admin_name', 'Quản trị viên')
        admin_role = request.form.get('admin_role', 'System Administrator')
        admin_email = request.form.get('admin_email', 'admin@system.com')

        session['admin_name'] = admin_name
        session['admin_role'] = admin_role
        session['admin_email'] = admin_email

        flash('Cập nhật thông tin Quản trị viên thành công!', 'success')
        return redirect(request.referrer or url_for('dashboard.index'))
    return redirect(url_for('dashboard.index'))
