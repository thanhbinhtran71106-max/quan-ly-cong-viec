from app import create_app, db
from app.models.employee import Employee
from app.models.task import Task
from app.models.schedule import Schedule
from datetime import date

app = create_app()

with app.app_context():
    # Lấy nhân viên
    nv_it = Employee.query.filter_by(code='NV001').first()
    nv_sale = Employee.query.filter_by(code='NV002').first()
    nv_hc = Employee.query.filter_by(code='NV003').first()

    # Lấy công việc
    cv_it1 = Task.query.filter_by(code='CV001').first() # 4h
    cv_it2 = Task.query.filter_by(code='CV002').first() # 6h
    
    cv_sale1 = Task.query.filter_by(code='CV003').first() # 4h
    cv_sale2 = Task.query.filter_by(code='CV004').first() # 4h
    
    cv_hc1 = Task.query.filter_by(code='CV005').first() # 2h
    cv_hc2 = Task.query.filter_by(code='CV006').first() # 4h

    today = date.today()

    schedules = [
        # NV001: 10 tiếng (Tăng ca Sáng, Chiều) + Ca Tối
        Schedule(employee_id=nv_it.id, task_id=cv_it1.id, date=today, shift='Sáng', status='Done', is_overtime=False),
        Schedule(employee_id=nv_it.id, task_id=cv_it2.id, date=today, shift='Chiều', status='In Progress', is_overtime=True),
        Schedule(employee_id=nv_it.id, task_id=cv_it2.id, date=today, shift='Tối', status='Todo', is_overtime=True),
        
        # NV002: 12 tiếng + Ca Tối
        Schedule(employee_id=nv_sale.id, task_id=cv_sale1.id, date=today, shift='Sáng', status='Todo', is_overtime=False),
        Schedule(employee_id=nv_sale.id, task_id=cv_sale2.id, date=today, shift='Chiều', status='Todo', is_overtime=False),
        Schedule(employee_id=nv_sale.id, task_id=cv_sale1.id, date=today, shift='Tối', status='Todo', is_overtime=True),

        # NV003: 10 tiếng + Ca Tối
        Schedule(employee_id=nv_hc.id, task_id=cv_hc1.id, date=today, shift='Sáng', status='Done', is_overtime=False),
        Schedule(employee_id=nv_hc.id, task_id=cv_hc2.id, date=today, shift='Chiều', status='Done', is_overtime=False),
        Schedule(employee_id=nv_hc.id, task_id=cv_hc2.id, date=today, shift='Tối', status='Todo', is_overtime=True),
    ]

    db.session.add_all(schedules)
    db.session.commit()
    print("Xong")
