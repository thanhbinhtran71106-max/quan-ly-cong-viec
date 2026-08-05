from app.sensor.repositories import SensorRepository, SensorTypeRepository, SensorDataRepository

class SensorService:
    def __init__(self):
        self.sensor_repo = SensorRepository()
        self.type_repo = SensorTypeRepository()
        self.data_repo = SensorDataRepository()

    def get_sensors(self, page=1, per_page=10, search_query=None, device_id=None):
        return self.sensor_repo.get_all(page, per_page, search_query, device_id)

    def get_sensor(self, sensor_id):
        return self.sensor_repo.get_by_id(sensor_id)

    def create_sensor(self, data):
        if 'name' not in data or 'type_name' not in data:
            raise ValueError("Tên sensor và loại sensor (type_name) là bắt buộc.")
        
        stype = self.type_repo.get_by_name(data['type_name'])
        if not stype:
            unit = data.get('unit', '')
            stype = self.type_repo.create(name=data['type_name'], unit=unit)
        
        sensor_data = {
            'name': data['name'],
            'type_id': stype.id,
            'device_id': data.get('device_id'),
            'pin_address': data.get('pin_address', ''),
            'status': data.get('status', 'active')
        }
        return self.sensor_repo.create(sensor_data)

    def update_sensor(self, sensor_id, data):
        sensor = self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise ValueError("Sensor không tồn tại")
        if 'type_name' in data:
            stype = self.type_repo.get_by_name(data['type_name'])
            if not stype:
                stype = self.type_repo.create(name=data['type_name'], unit=data.get('unit', ''))
            data['type_id'] = stype.id
            del data['type_name']
        return self.sensor_repo.update(sensor, data)

    def delete_sensor(self, sensor_id):
        sensor = self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise ValueError("Sensor không tồn tại")
        return self.sensor_repo.delete(sensor)

    def record_data(self, sensor_id, value):
        sensor = self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise ValueError("Sensor không tồn tại")
        
        # Áp dụng hiệu chuẩn (Calibration Offset) nếu có cấu hình
        calibrated_value = value + (sensor.calibration_offset or 0.0)
        return self.data_repo.add_reading(sensor_id, calibrated_value)

    def get_sensor_chart_data(self, sensor_id, limit=50):
        sensor = self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise ValueError("Sensor không tồn tại")
        history = self.data_repo.get_history(sensor_id, limit)
        return {
            'sensor': sensor.to_dict(),
            'labels': [item.timestamp.strftime('%H:%M:%S') for item in history],
            'values': [item.value for item in history]
        }

    def get_all_types(self):
        return [t.to_dict() for t in self.type_repo.get_all()]
