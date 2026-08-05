from app.sensor.models import Sensor, SensorType, SensorData
from app import db
from sqlalchemy import or_

class SensorTypeRepository:
    def get_all(self):
        return SensorType.query.all()

    def get_by_id(self, type_id):
        return db.session.get(SensorType, type_id)

    def get_by_name(self, name):
        return SensorType.query.filter_by(name=name).first()

    def create(self, name, unit, description=""):
        stype = SensorType(name=name, unit=unit, description=description)
        db.session.add(stype)
        db.session.commit()
        return stype

class SensorRepository:
    def get_all(self, page=1, per_page=10, search_query=None, device_id=None):
        query = Sensor.query
        if device_id:
            query = query.filter_by(device_id=device_id)
        if search_query:
            query = query.filter(or_(
                Sensor.name.ilike(f"%{search_query}%"),
                Sensor.pin_address.ilike(f"%{search_query}%")
            ))
        return query.order_by(Sensor.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_by_id(self, sensor_id):
        return db.session.get(Sensor, sensor_id)

    def create(self, data):
        sensor = Sensor(**data)
        db.session.add(sensor)
        db.session.commit()
        return sensor

    def update(self, sensor, data):
        for key, value in data.items():
            if hasattr(sensor, key):
                setattr(sensor, key, value)
        db.session.commit()
        return sensor

    def delete(self, sensor):
        db.session.delete(sensor)
        db.session.commit()

class SensorDataRepository:
    def add_reading(self, sensor_id, value):
        data = SensorData(sensor_id=sensor_id, value=value)
        db.session.add(data)
        db.session.commit()
        return data

    def get_history(self, sensor_id, limit=50):
        return SensorData.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorData.timestamp.asc())\
            .limit(limit).all()
