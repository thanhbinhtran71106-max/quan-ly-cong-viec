from app import db
from datetime import datetime, timezone

class DeviceType(db.Model):
    __tablename__ = 'device_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # VD: ESP32, STM32, PLC
    description = db.Column(db.String(255))
    
    devices = db.relationship('Device', backref='type_ref', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'), nullable=False)
    status = db.Column(db.String(50), default='offline')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    topics = db.relationship('MqttTopic', backref='device', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type_ref.name if self.type_ref else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'topics': [t.to_dict() for t in self.topics]
        }

class MqttTopic(db.Model):
    __tablename__ = 'mqtt_topics'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    direction = db.Column(db.String(10), nullable=False) # 'pub' hoặc 'sub'
    qos = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {'id': self.id, 'topic': self.topic, 'direction': self.direction, 'qos': self.qos}
