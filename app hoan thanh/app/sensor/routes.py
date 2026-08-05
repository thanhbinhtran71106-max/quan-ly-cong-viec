from flask import jsonify, request, render_template
from app.sensor import sensor_bp
from app.sensor.services import SensorService
from app.auth.decorators import token_required

sensor_service = SensorService()

@sensor_bp.route('/api/sensors', methods=['GET'])
def get_sensors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    search_query = request.args.get('search', None)
    device_id = request.args.get('device_id', None, type=int)

    pagination = sensor_service.get_sensors(page, per_page, search_query, device_id)
    return jsonify({
        'data': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@sensor_bp.route('/api/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    sensor = sensor_service.get_sensor(sensor_id)
    if not sensor:
        return jsonify({'error': 'Không tìm thấy sensor'}), 404
    return jsonify(sensor.to_dict()), 200

@sensor_bp.route('/api/sensors', methods=['POST'])
def create_sensor():
    try:
        data = request.get_json()
        sensor = sensor_service.create_sensor(data)
        return jsonify(sensor.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@sensor_bp.route('/api/sensors/<int:sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    try:
        data = request.get_json()
        sensor = sensor_service.update_sensor(sensor_id, data)
        return jsonify(sensor.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@sensor_bp.route('/api/sensors/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    try:
        sensor_service.delete_sensor(sensor_id)
        return jsonify({'message': 'Xóa sensor thành công'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

from app.sensor.ai_service import AIService
ai_service = AIService()

@sensor_bp.route('/api/sensors/<int:sensor_id>/data', methods=['POST'])
def add_sensor_data(sensor_id):
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'error': 'Thiếu giá trị value'}), 400
    try:
        val = float(data['value'])
        reading = sensor_service.record_data(sensor_id, val)
        sensor = sensor_service.get_sensor(sensor_id)
        
        # Bắn sự kiện thời gian thực SocketIO để giao diện lập tức nhận phản hồi khi giả lập
        from app import socketio
        socketio.emit('sensor_telemetry_update', {
            'sensor_id': sensor_id,
            'value': val,
            'unit': sensor.type_ref.unit if sensor and sensor.type_ref else '',
            'timestamp': reading.timestamp.strftime('%H:%M:%S')
        })
        
        # Kiểm tra chế độ AI Autopilot (Điều khiển dự đoán thông minh)
        ai_action, predicted = ai_service.analyze_and_autopilot(sensor_id, val)
        if ai_action == "fan_on":
            from app.auth.services import AuthService
            AuthService().log_action(None, "AI Autopilot", f"AI phân tích xu hướng tăng nhiệt dự đoán đạt {predicted} °C. Tự động kích hoạt quạt thông gió để bảo vệ thiết bị.")
            
            # Gửi tín hiệu kích hoạt quạt cho client qua SocketIO
            socketio.emit('ai_autopilot_trigger', {
                'action': 'fan_on',
                'predicted_temp': predicted,
                'target_temp': 26.5
            })
        
        return jsonify(reading.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/api/sensors/<int:sensor_id>/chart', methods=['GET'])
def get_sensor_chart(sensor_id):
    limit = request.args.get('limit', 50, type=int)
    try:
        chart_data = sensor_service.get_sensor_chart_data(sensor_id, limit)
        return jsonify(chart_data), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@sensor_bp.route('/api/sensors/<int:sensor_id>/export', methods=['GET'])
@token_required
def export_sensor_data(current_user, sensor_id):
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        sensor = sensor_service.get_sensor(sensor_id)
        if not sensor:
            return jsonify({'error': 'Không tìm thấy cảm biến'}), 404
            
        history = sensor_service.data_repo.get_history(sensor_id, limit=1000)
        
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', 'Sensor Name', 'Value', 'Unit', 'Timestamp'])
        for item in history:
            cw.writerow([
                item.id,
                sensor.name,
                item.value,
                sensor.type_ref.unit if sensor.type_ref else '',
                item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
            
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=sensor_{sensor_id}_data.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/sensors', methods=['GET'])
@token_required
def sensor_page(current_user):
    return render_template('sensors.html', current_user=current_user)

@sensor_bp.route('/distance', methods=['GET'])
@token_required
def distance_page(current_user):
    return render_template('distance.html', current_user=current_user)

@sensor_bp.route('/api/ai/autopilot', methods=['POST'])
@token_required
def toggle_ai_autopilot(current_user):
    try:
        data = request.get_json()
        status = data.get('active', False)
        active = ai_service.toggle_autopilot(status)
        
        from app.auth.services import AuthService
        AuthService().log_action(current_user.id, "Bật AI Autopilot" if active else "Tắt AI Autopilot", 
                                 f"Quản trị viên đã {'bật' if active else 'tắt'} chế độ AI Tự động hóa hệ thống.")
                                 
        return jsonify({'active': active}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/api/ai/autopilot/status', methods=['GET'])
@token_required
def get_ai_autopilot_status(current_user):
    return jsonify({'active': ai_service.autopilot_active}), 200

@sensor_bp.route('/api/ai/chat', methods=['POST'])
@token_required
def ai_chat(current_user):
    try:
        data = request.get_json()
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Thiếu nội dung câu hỏi'}), 400
        response = ai_service.get_ai_chat_response(message)
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

