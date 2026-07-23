from app import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    base_salary_per_hour = db.Column(db.Integer, nullable=False, default=50000) # VD: 50.000 VNĐ/giờ
    promotion_proposal = db.Column(db.Text, nullable=True) # Đề xuất thăng tiến

    schedules = db.relationship('Schedule', backref='employee', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'fullname': self.fullname,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
            'base_salary_per_hour': self.base_salary_per_hour,
            'promotion_proposal': self.promotion_proposal or ''
        }
