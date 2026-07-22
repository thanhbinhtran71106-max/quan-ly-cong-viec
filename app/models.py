from datetime import datetime
from app import db


class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship('Schedule', backref='employee', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Employee {self.employee_code} - {self.full_name}>'

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


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    task_code = db.Column(db.String(20), unique=True, nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    duration = db.Column(db.Float, nullable=False, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship('Schedule', backref='task', lazy=True, cascade='all, delete-orphan')

    PRIORITY_CHOICES = ['Low', 'Medium', 'High', 'Critical']

    def __repr__(self):
        return f'<Task {self.task_code} - {self.task_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'task_code': self.task_code,
            'task_name': self.task_name,
            'description': self.description,
            'priority': self.priority,
            'duration': self.duration,
        }


class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(10), nullable=False)  # 'morning' or 'afternoon'
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    SHIFT_LABELS = {
        'morning': 'Ca Sáng (07:30 - 11:30)',
        'afternoon': 'Ca Chiều (13:00 - 17:00)',
    }

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'work_date', 'shift', name='uq_employee_date_shift'),
    )

    def __repr__(self):
        return f'<Schedule emp={self.employee_id} task={self.task_id} date={self.work_date} shift={self.shift}>'

    @property
    def shift_label(self):
        return self.SHIFT_LABELS.get(self.shift, self.shift)

    @property
    def day_of_week(self):
        days = {0: 'Thứ Hai', 1: 'Thứ Ba', 2: 'Thứ Tư',
                3: 'Thứ Năm', 4: 'Thứ Sáu', 5: 'Thứ Bảy'}
        return days.get(self.work_date.weekday(), '')
