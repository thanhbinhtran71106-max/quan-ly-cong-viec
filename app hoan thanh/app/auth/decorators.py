from functools import wraps
from flask import request, jsonify, redirect, url_for
import jwt
from flask import current_app
from app.auth.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 1. Kiểm tra trong Authorization Header (Cho REST API)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        # 2. Kiểm tra trong Cookie (Cho Web Browser Dashboard)
        if not token and 'jwt_token' in request.cookies:
            token = request.cookies.get('jwt_token')
            
        if not token:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Truy cập bị từ chối. Vui lòng gửi JWT Token!'}), 401
            return redirect(url_for('auth.login_page'))
            
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['sub'])
            if not current_user:
                raise ValueError("Người dùng không tồn tại")
        except Exception:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Token không hợp lệ hoặc đã hết hạn!'}), 401
            return redirect(url_for('auth.login_page'))
            
        return f(current_user, *args, **kwargs)
    return decorated
