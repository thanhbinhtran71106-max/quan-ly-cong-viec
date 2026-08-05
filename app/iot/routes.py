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

from app.iot.models import DeviceState
from app import db

@iot_bp.route('/led', methods=['POST'])
def update_led_state():
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        state = data.get('state')
        
        if device_id and state in [0, 1]:
            led = DeviceState.query.filter_by(device_id=device_id).first()
            if not led:
                led = DeviceState(device_id=device_id, led_state=state)
                db.session.add(led)
            else:
                led.led_state = state
            db.session.commit()
            
            # Phát sóng socketio báo trạng thái đổi
            from app import socketio
            pin_num = 4
            if '_' in device_id:
                try:
                    pin_num = int(device_id.split('_')[1])
                except:
                    pass
            socketio.emit('ai_control_trigger', {
                'action': 'fan_on' if state == 1 else 'power_off',
                'pin': pin_num
            })
            
            return jsonify({"status": "success", "message": f"{device_id} state updated to {state}"}), 200
        return jsonify({"status": "error", "message": "Invalid params"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@iot_bp.route('/led', methods=['GET'])
def get_led_state():
    try:
        rows = DeviceState.query.all()
        res = {}
        for r in rows:
            res[r.device_id] = r.led_state
            if r.device_id.startswith("led_"):
                pin_num = r.device_id.split("_")[1]
                res[pin_num] = r.led_state
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
