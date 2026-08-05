from app.iot.repositories import DeviceRepository, DeviceTypeRepository, MqttTopicRepository

class DeviceService:
    def __init__(self):
        self.device_repo = DeviceRepository()
        self.type_repo = DeviceTypeRepository()
        self.topic_repo = MqttTopicRepository()
        
    def get_devices(self, page, per_page, search_query):
        return self.device_repo.get_all(page, per_page, search_query)
        
    def get_device(self, device_id):
        return self.device_repo.get_by_id(device_id)
        
    def create_device(self, data):
        if 'name' not in data or 'type_name' not in data:
            raise ValueError("Tên và loại thiết bị là bắt buộc.")
            
        # Xử lý tự động sinh/tìm DeviceType
        dtype = self.type_repo.get_by_name(data['type_name'])
        if not dtype:
            dtype = self.type_repo.create(name=data['type_name'])
            
        device_data = {
            'name': data['name'],
            'type_id': dtype.id,
            'status': data.get('status', 'offline')
        }
        
        device = self.device_repo.create(device_data)
        
        # Thêm các MQTT Topic nếu có
        topics = data.get('topics', [])
        for t in topics:
            if 'topic' in t and 'direction' in t:
                self.topic_repo.create(
                    device_id=device.id,
                    topic=t['topic'],
                    direction=t['direction'],
                    qos=t.get('qos', 0)
                )
            
        return device

    def update_device(self, device_id, data):
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise ValueError("Không tìm thấy thiết bị")
            
        if 'type_name' in data:
            dtype = self.type_repo.get_by_name(data['type_name'])
            if not dtype:
                dtype = self.type_repo.create(name=data['type_name'])
            data['type_id'] = dtype.id
            del data['type_name']
            
        if 'topics' in data:
            del data['topics'] # Sẽ xử lý topic rời (nếu cần)
            
        return self.device_repo.update(device, data)
        
    def delete_device(self, device_id):
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise ValueError("Không tìm thấy thiết bị")
        self.device_repo.delete(device)
