import json
import logging
from paho.mqtt import client as mqtt
from app import db, socketio
from app.sensor.services import SensorService
from app.iot.services import DeviceService

logger = logging.getLogger(__name__)

class MQTTService:
    def __init__(self, app=None):
        self.app = app
        self.client = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        
        # Paho MQTT v2.x client creation requires CallbackAPIVersion
        try:
            self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        except AttributeError:
            self.client = mqtt.Client() # Fallback for older paho-mqtt versions

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        broker = app.config.get('MQTT_BROKER_URL', 'localhost')
        port = app.config.get('MQTT_BROKER_PORT', 1883)
        keepalive = app.config.get('MQTT_KEEPALIVE', 60)

        try:
            # Kết nối bất đồng bộ
            self.client.connect_async(broker, port, keepalive)
            # Khởi động vòng lặp MQTT chạy ngầm
            self.client.loop_start()
            print(f"[*] MQTT Service: Connecting to broker {broker}:{port}...")
        except Exception as e:
            print(f"[!] MQTT Service: Connection failed: {e}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("[*] MQTT Service: Connected successfully to broker.")
        # Đăng ký nhận status của thiết bị: v1/devices/<device_id>/status
        client.subscribe("v1/devices/+/status")
        # Đăng ký nhận dữ liệu cảm biến: v1/devices/<device_id>/sensors/<sensor_id>/telemetry
        client.subscribe("v1/devices/+/sensors/+/telemetry")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        topic = msg.topic
        print(f"[*] MQTT Received: {topic} -> {payload}")

        # Thao tác CSDL yêu cầu Flask Application Context
        with self.app.app_context():
            try:
                parts = topic.split('/')
                
                # 1. Xử lý cập nhật trạng thái thiết bị
                # Topic: v1/devices/<device_id>/status
                if len(parts) == 4 and parts[3] == 'status':
                    device_id = int(parts[2])
                    try:
                        status_data = json.loads(payload)
                        status = status_data.get('status', 'offline')
                    except json.JSONDecodeError:
                        status = payload
                    
                    device_service = DeviceService()
                    device_service.update_device(device_id, {'status': status})
                    
                    # Bắn sự kiện thời gian thực qua SocketIO về Web UI Dashboard
                    socketio.emit('device_status_update', {
                        'device_id': device_id,
                        'status': status
                    })
                    print(f"[*] Broadcasted status update for device {device_id}: {status}")

                # 2. Xử lý cập nhật số liệu cảm biến (Telemetry)
                # Topic: v1/devices/<device_id>/sensors/<sensor_id>/telemetry
                elif len(parts) == 6 and parts[5] == 'telemetry':
                    device_id = int(parts[2])
                    sensor_id = int(parts[4])
                    try:
                        data = json.loads(payload)
                        value = float(data.get('value', 0))
                    except (json.JSONDecodeError, ValueError):
                        value = float(payload)

                    sensor_service = SensorService()
                    reading = sensor_service.record_data(sensor_id, value)
                    sensor = sensor_service.get_sensor(sensor_id)
                    
                    # Bắn số liệu cảm biến thời gian thực qua SocketIO để vẽ biểu đồ tự động
                    socketio.emit('sensor_telemetry_update', {
                        'sensor_id': sensor_id,
                        'value': value,
                        'unit': sensor.type_ref.unit if sensor and sensor.type_ref else '',
                        'timestamp': reading.timestamp.strftime('%H:%M:%S')
                    })
                    print(f"[*] Broadcasted sensor {sensor_id} value: {value}")

            except Exception as e:
                print(f"[!] MQTT Handle Message Error: {e}")

    def publish_command(self, topic, payload):
        if self.client and self.client.is_connected():
            self.client.publish(topic, json.dumps(payload))
            return True
        return False
