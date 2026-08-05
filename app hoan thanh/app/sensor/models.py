from app import db
from datetime import datetime, timezone

class SensorType(db.Model):
    __tablename__ = 'sensor_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., Temperature, Humidity, Pressure, CO2
    unit = db.Column(db.String(20), nullable=False) # e.g., °C, %, hPa, ppm
    description = db.Column(db.String(255))
    
    sensors = db.relationship('Sensor', backref='type_ref', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'unit': self.unit, 'description': self.description}

class Sensor(db.Model):
    __tablename__ = 'sensors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('sensor_types.id'), nullable=False)
    pin_address = db.Column(db.String(50)) # e.g., GPIO15, I2C 0x68
    calibration_offset = db.Column(db.Float, default=0.0) # Hiệu chuẩn cảm biến
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    readings = db.relationship('SensorData', backref='sensor', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        latest = SensorData.query.filter_by(sensor_id=self.id).order_by(SensorData.timestamp.desc()).first()
        return {
            'id': self.id,
            'name': self.name,
            'device_id': self.device_id,
            'type': self.type_ref.name if self.type_ref else None,
            'unit': self.type_ref.unit if self.type_ref else '',
            'pin_address': self.pin_address,
            'calibration_offset': self.calibration_offset,
            'status': self.status,
            'latest_value': latest.value if latest else None,
            'latest_timestamp': latest.timestamp.isoformat() if latest and latest.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
