from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register Blueprints here
    from app.iot import iot_bp
    app.register_blueprint(iot_bp, url_prefix='/api/iot')
    
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from app.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.sensor import sensor_bp
    app.register_blueprint(sensor_bp)

    with app.app_context():
        from app.auth.models import User, Role
        from app.iot.models import Device, DeviceType, MqttTopic
        from app.sensor.models import Sensor, SensorType, SensorData
        db.create_all()
        
        from app.auth.services import AuthService
        AuthService().seed_default_admin()

        # Khởi tạo sẵn Cấu hình Device Type và Device cho mô hình hệ thống hoạt động
        try:
            # 1. Tạo loại thiết bị
            esp32_type = DeviceType.query.filter_by(name='ESP32').first()
            if not esp32_type:
                esp32_type = DeviceType(name='ESP32', description='Node vi điều khiển ESP32 AIoT')
                db.session.add(esp32_type)
            
            stm32_type = DeviceType.query.filter_by(name='STM32').first()
            if not stm32_type:
                stm32_type = DeviceType(name='STM32', description='Weather Station STM32')
                db.session.add(stm32_type)
                
            db.session.commit()
            
            # 2. Tạo thiết bị mẫu
            dev1 = Device.query.get(1)
            if not dev1:
                dev1 = Device(id=1, name='ESP32 Sensor Hub Node 1', type_id=esp32_type.id, status='online')
                db.session.add(dev1)
                
            dev2 = Device.query.get(2)
            if not dev2:
                dev2 = Device(id=2, name='STM32 Climate Node 2', type_id=stm32_type.id, status='online')
                db.session.add(dev2)
                
            db.session.commit()
        except Exception as ex:
            print(f"Error seeding devices: {ex}")

        # Khởi tạo sẵn Cảm biến 1, 2 và 3 trong CSDL phục vụ cho bộ giả lập (Simulator)
        from app.sensor.services import SensorService
        from app.iot.models import DeviceState
        sensor_service = SensorService()
        try:
            if not sensor_service.get_sensor(1):
                sensor_service.create_sensor({
                    'name': 'DHT22 - Nhiệt Độ',
                    'type_name': 'Temperature',
                    'unit': '°C',
                    'pin_address': 'GPIO14',
                    'device_id': 1
                })
            if not sensor_service.get_sensor(2):
                sensor_service.create_sensor({
                    'name': 'DHT22 - Độ Ẩm',
                    'type_name': 'Humidity',
                    'unit': '%',
                    'pin_address': 'GPIO14',
                    'device_id': 1
                })
            if not sensor_service.get_sensor(3):
                sensor_service.create_sensor({
                    'name': 'BMP280 - Áp Suất',
                    'type_name': 'Pressure',
                    'unit': 'hPa',
                    'pin_address': 'I2C 0x76',
                    'device_id': 2
                })
            
            # Seeding DeviceState cho 8 LED và sensor_auto
            for pin in [4, 5, 6, 7, 15, 16, 17, 18]:
                led_id = f"led_{pin}"
                if not DeviceState.query.filter_by(device_id=led_id).first():
                    db.session.add(DeviceState(device_id=led_id, led_state=0))
            if not DeviceState.query.filter_by(device_id='sensor_auto').first():
                db.session.add(DeviceState(device_id='sensor_auto', led_state=1))
            db.session.commit()
            
        except Exception as e:
            print(f"Error seeding sensors and device states: {e}")

        from app.iot.mqtt_service import MQTTService
        app.mqtt_service = MQTTService(app)

    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'AIoT Server is running'}

    @app.route('/')
    def index():
        return redirect('/dashboard')

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app
