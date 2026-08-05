import jwt
from datetime import datetime, timedelta, timezone
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app.auth.repositories import UserRepository, RoleRepository, AuditLogRepository

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()
        self.audit_repo = AuditLogRepository()
        
    def seed_default_admin(self):
        if not self.user_repo.get_by_username('admin'):
            admin_user = self.register_user('admin', 'admin123', 'admin')
            admin_user.email = 'admin@aiot.com'
            from app import db
            db.session.commit()
            
            # Seeding 25 nhân viên vận hành hệ thống ngẫu nhiên
            import random
            
            names = ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Minh Đức", 
                     "Vũ Anh Dũng", "Hoàng Kim Liên", "Ngô Quốc Khánh", "Đỗ Hải Yến", 
                     "Bùi Quang Huy", "Phan Thanh Sơn", "Dương Minh Anh", "Lý Gia Bảo", 
                     "Võ Hoài Nam", "Đặng Thùy Chi", "Nguyễn Hồng Ngọc", "Trần Tiến Đạt", 
                     "Lê Thu Trang", "Phạm Văn Nam", "Vũ Hoàng Long", "Hoàng Mai Hương",
                     "Nguyễn Tấn Tài", "Trần Văn Phú", "Lê Minh Triết", "Vũ Tuyết Mai", "Đỗ Văn Dũng"]
                     
            usernames = ["an.nv", "binh.tt", "cuong.lh", "duc.pm", "dung.va", "lien.hk", 
                         "khanh.nq", "yen.dh", "huy.bq", "son.pt", "anh.dm", "bao.lg", 
                         "nam.vh", "chi.dt", "ngoc.nh", "dat.tt", "trang.lt", "nam.pv", 
                         "long.vh", "huong.hm", "tai.nt", "phu.tv", "triet.lm", "mai.vt", "dung.dv"]
                         
            actions = [
                ("Đăng Nhập", "Nhân viên đăng nhập thành công vào bảng điều khiển."),
                ("Kích Hoạt Thiết Bị", "Đã bật thiết bị Quạt thông gió làm mát."),
                ("Ngắt Nguồn", "Ngắt nguồn khẩn cấp Thiết bị IoT do cảnh báo quá nhiệt."),
                ("Đăng Xuất", "Nhân viên đăng xuất khỏi hệ thống."),
                ("Cập Nhật Cấu Hinh", "Thay đổi ngưỡng nhiệt độ cảnh báo thành 35 độ C."),
                ("Cập Nhật Firmware OTA", "Đã gửi yêu cầu cập nhật Firmware bản v2.1.3 lên Node ESP32.")
            ]
            
            role = self.role_repo.get_by_name('user')
            if not role:
                role = self.role_repo.create('user')
                
            for i in range(len(names)):
                uname = usernames[i]
                fullname = names[i]
                email = f"{uname}@aiot.com"
                
                if not self.user_repo.get_by_username(uname):
                    user_data = {
                        'username': fullname,
                        'email': email,
                        'password_hash': generate_password_hash("user123"),
                        'role_id': role.id
                    }
                    user = self.user_repo.create(user_data)
                    
                    # Tạo ngẫu nhiên 2-3 log hoạt động cách đây vài giờ/ngày
                    for _ in range(random.randint(2, 3)):
                        act, det = random.choice(actions)
                        log_time = datetime.now() - timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
                        ip = f"192.168.1.{random.randint(10, 99)}"
                        self.audit_repo.create(user.id, act, f"{det} (Nhân viên: {fullname})", ip, log_time)
            
            db.session.commit()

    def register_user(self, username, password, role_name='user'):
        if self.user_repo.get_by_username(username):
            raise ValueError("Tên đăng nhập đã tồn tại")
            
        role = self.role_repo.get_by_name(role_name)
        if not role:
            role = self.role_repo.create(role_name)
            
        hashed_password = generate_password_hash(password)
        user = self.user_repo.create({
            'username': username,
            'password_hash': hashed_password,
            'role_id': role.id
        })
        
        # Log action
        self.log_action(None, "Đăng Ký", f"Người dùng mới {username} đăng ký tài khoản.")
        return user
        
    def login(self, username, password):
        user = self.user_repo.get_by_username(username)
        if not user or not check_password_hash(user.password_hash, password):
            # Log failed login attempt
            self.log_action(None, "Đăng Nhập Thất Bại", f"Thử đăng nhập sai mật khẩu tài khoản: {username}")
            raise ValueError("Tên đăng nhập hoặc mật khẩu không chính xác")
            
        token = jwt.encode({
            'sub': user.id,
            'username': user.username,
            'role': user.role.name,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        # Log success login
        self.log_action(user.id, "Đăng Nhập", f"Người dùng {username} đăng nhập thành công.")
        
        return token

    def log_action(self, user_id, action, details):
        # Trích xuất IP
        ip_addr = request.remote_addr if request else '127.0.0.1'
        self.audit_repo.create(user_id, action, details, ip_addr)

    def get_logs(self, page=1, per_page=15):
        return self.audit_repo.get_all(page, per_page)
