from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship('Schedule', backref='employee', lazy=True,
                                cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_code': self.employee_code,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
        }

    def __repr__(self):
        return f'<Employee {self.employee_code} - {self.full_name}>'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    task_code = db.Column(db.String(20), unique=True, nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default='medium')  # low / medium / high
    duration = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship('Schedule', backref='task', lazy=True,
                                cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'task_code': self.task_code,
            'task_name': self.task_name,
            'description': self.description,
            'priority': self.priority,
            'duration': self.duration,
        }

    def __repr__(self):
        return f'<Task {self.task_code} - {self.task_name}>'


class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(10), nullable=False)  # 'morning' / 'afternoon'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ràng buộc: 1 nhân viên không được trùng ca trong cùng 1 ngày
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'work_date', 'shift',
                            name='uq_employee_date_shift'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name,
            'task_id': self.task_id,
            'task_name': self.task.task_name,
            'work_date': self.work_date.strftime('%Y-%m-%d'),
            'shift': self.shift,
        }

    def __repr__(self):
        return f'<Schedule {self.employee_id} - {self.work_date} - {self.shift}>'
