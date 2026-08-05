from app.iot.models import Device, DeviceType, MqttTopic
from app import db
from sqlalchemy import or_

class DeviceRepository:
    def get_all(self, page=1, per_page=10, search_query=None):
        query = Device.query
        
        if search_query:
            query = query.filter(or_(
                Device.name.ilike(f"%{search_query}%"),
                Device.status.ilike(f"%{search_query}%")
            ))
            
        pagination = query.order_by(Device.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pagination
        
    def get_by_id(self, device_id):
        return db.session.get(Device, device_id)
        
    def create(self, data):
        device = Device(**data)
        db.session.add(device)
        db.session.commit()
        return device
        
    def update(self, device, data):
        for key, value in data.items():
            if hasattr(device, key):
                setattr(device, key, value)
        db.session.commit()
        return device
        
    def delete(self, device):
        db.session.delete(device)
        db.session.commit()

class DeviceTypeRepository:
    def get_by_name(self, name):
        return DeviceType.query.filter_by(name=name).first()
        
    def create(self, name, description=""):
        dtype = DeviceType(name=name, description=description)
        db.session.add(dtype)
        db.session.commit()
        return dtype

class MqttTopicRepository:
    def create(self, device_id, topic, direction, qos=0):
        t = MqttTopic(device_id=device_id, topic=topic, direction=direction, qos=qos)
        db.session.add(t)
        db.session.commit()
        return t
