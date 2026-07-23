from app import db

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='Trung bình') # Cao, Trung bình, Thường
    duration = db.Column(db.Integer, nullable=False, default=4) # Hours
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    required_expertise = db.Column(db.String(50), nullable=True)

    schedules = db.relationship('Schedule', backref='task', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'task_name': self.task_name,
            'priority': self.priority,
            'duration': self.duration,
            'description': self.description or '',
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'required_expertise': self.required_expertise or ''
        }
