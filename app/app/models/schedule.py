from app import db
from datetime import date

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    shift = db.Column(db.String(20), nullable=False) # 'Sáng', 'Chiều'
    status = db.Column(db.String(20), nullable=False, default='Todo') # 'Todo', 'In Progress', 'Done'

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'task_id': self.task_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'shift': self.shift,
            'status': self.status
        }
