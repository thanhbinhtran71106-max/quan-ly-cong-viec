from app.auth.models import User, Role, AuditLog
from app import db

class UserRepository:
    def get_by_username(self, username):
        return User.query.filter_by(username=username).first()
        
    def create(self, data):
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user

class RoleRepository:
    def get_by_name(self, name):
        return Role.query.filter_by(name=name).first()
        
    def create(self, name):
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
        return role

class AuditLogRepository:
    def create(self, user_id, action, details, ip_address, timestamp=None):
        log = AuditLog(user_id=user_id, action=action, details=details, ip_address=ip_address, timestamp=timestamp)
        db.session.add(log)
        db.session.commit()
        return log
        
    def get_all(self, page=1, per_page=15):
        return AuditLog.query.order_by(AuditLog.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
