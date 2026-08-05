from flask import jsonify, request, render_template, redirect, url_for, make_response
from app.auth import auth_bp
from app.auth.services import AuthService
from app.auth.decorators import token_required

auth_service = AuthService()

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Thiếu tên đăng nhập hoặc mật khẩu'}), 400
        
    try:
        user = auth_service.register_user(data['username'], data['password'])
        return jsonify({'message': 'Đăng ký tài khoản thành công', 'user_id': user.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        
    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'Thiếu username hoặc password'}), 400
        return render_template('login.html', error='Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!')
        
    try:
        token = auth_service.login(username, password)
        if request.is_json:
            return jsonify({'token': token, 'message': 'Đăng nhập thành công'}), 200
        
        # Chuyển hướng Dashboard và set cookie
        resp = make_response(redirect(url_for('dashboard.index')))
        resp.set_cookie('jwt_token', token, httponly=True, samesite='Lax')
        return resp
    except ValueError as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 401
        return render_template('login.html', error=str(e))

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Log action trước khi xóa cookie/session
    token = request.cookies.get('jwt_token')
    if token:
        try:
            import jwt
            from flask import current_app
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            auth_service.log_action(data['sub'], "Đăng Xuất", f"Người dùng {data['username']} đã đăng xuất.")
        except Exception:
            pass

    resp = make_response(redirect(url_for('auth.login_page')))
    resp.set_cookie('jwt_token', '', expires=0)
    if request.is_json:
        return jsonify({'message': 'Đã đăng xuất thành công'}), 200
    return resp

# Route hiển thị Lịch sử hoạt động trên Web UI
@auth_bp.route('/logs', methods=['GET'])
@token_required
def logs_page(current_user):
    page = request.args.get('page', 1, type=int)
    pagination = auth_service.get_logs(page=page, per_page=15)
    return render_template('logs.html', pagination=pagination, current_user=current_user)

# REST API Lấy danh sách Logs
@auth_bp.route('/api/logs', methods=['GET'])
@token_required
def get_api_logs(current_user):
    page = request.args.get('page', 1, type=int)
    pagination = auth_service.get_logs(page=page, per_page=15)
    return jsonify({
        'data': [l.to_dict() for l in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

# REST API Ghi log hành động tùy chỉnh từ Web UI
@auth_bp.route('/log', methods=['POST'])
@token_required
def log_custom_action(current_user):
    try:
        data = request.get_json()
        action = data.get('action')
        details = data.get('details')
        if not action or not details:
            return jsonify({'error': 'Thiếu hành động hoặc mô tả chi tiết'}), 400
        
        auth_service.log_action(current_user.id, action, details)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# REST API Lấy Hồ sơ cá nhân
@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'role': current_user.role.name if current_user.role else None,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None
    }), 200

# REST API Đổi mật khẩu bảo mật
@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': 'Thiếu mật khẩu cũ hoặc mới'}), 400
            
        from werkzeug.security import check_password_hash, generate_password_hash
        if not check_password_hash(current_user.password_hash, old_password):
            return jsonify({'error': 'Mật khẩu cũ không chính xác'}), 400
            
        current_user.password_hash = generate_password_hash(new_password)
        from app import db
        db.session.commit()
        
        auth_service.log_action(current_user.id, "Đổi Mật Khẩu", f"Người dùng {current_user.username} đổi mật khẩu thành công.")
        return jsonify({'message': 'Thay đổi mật khẩu thành công'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


