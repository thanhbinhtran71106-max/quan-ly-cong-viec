from flask import jsonify, request
from app.iot import iot_bp
from app.iot.services import DeviceService

device_service = DeviceService()

@iot_bp.route('/devices', methods=['GET'])
def get_devices():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    search_query = request.args.get('search', None)
    
    pagination = device_service.get_devices(page, per_page, search_query)
    
    return jsonify({
        'data': [d.to_dict() for d in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page
    }), 200

@iot_bp.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = device_service.get_device(device_id)
    if not device:
        return jsonify({'error': 'Không tìm thấy thiết bị'}), 404
    return jsonify(device.to_dict()), 200

@iot_bp.route('/devices', methods=['POST'])
def create_device():
    try:
        data = request.get_json()
        device = device_service.create_device(data)
        return jsonify(device.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Lỗi hệ thống', 'details': str(e)}), 500

@iot_bp.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    try:
        data = request.get_json()
        device = device_service.update_device(device_id, data)
        return jsonify(device.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@iot_bp.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        device_service.delete_device(device_id)
        return jsonify({'message': 'Đã xóa thiết bị thành công'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
