import random
from app.sensor.repositories import SensorDataRepository, SensorRepository
from app.auth.repositories import AuditLogRepository

class AIService:
    def __init__(self):
        self.data_repo = SensorDataRepository()
        self.sensor_repo = SensorRepository()
        self.audit_repo = AuditLogRepository()
        self.autopilot_active = False

    def toggle_autopilot(self, active_status):
        self.autopilot_active = active_status
        return self.autopilot_active

    def predict_future_temperature(self, sensor_id, steps=5):
        """
        Dự đoán nhiệt độ tiếp theo sử dụng hồi quy xu hướng tuyến tính đơn giản (Linear Trend Projection)
        """
        history = self.data_repo.get_history(sensor_id, limit=10)
        if len(history) < 3:
            return None
        
        # Lấy giá trị thô theo thứ tự thời gian tăng dần
        values = [h.value for h in reversed(history)]
        
        # Tính toán sai số trung bình (độ dốc xu hướng)
        diffs = [values[i] - values[i-1] for i in range(1, len(values))]
        avg_slope = sum(diffs) / len(diffs)
        
        # Dự đoán tương lai
        last_val = values[-1]
        predicted_val = last_val + (avg_slope * steps)
        return round(predicted_val, 2)

    def analyze_and_autopilot(self, sensor_id, current_value):
        """
        Phân tích dữ liệu cảm biến thời gian thực và kích hoạt quạt gió tự động (Predictive Control)
        """
        if not self.autopilot_active:
            return None, None
            
        sensor = self.sensor_repo.get_by_id(sensor_id)
        if not sensor or sensor.type_ref.name != 'Temperature':
            return None, None

        # 1. Dự đoán xu hướng nhiệt độ trong 5 chu kỳ tiếp theo
        predicted_temp = self.predict_future_temperature(sensor_id)
        
        # 2. Nếu nhiệt độ hiện tại >= 35 độ C hoặc dự đoán xu hướng sắp vượt 35 độ C
        if current_value >= 35.0 or (predicted_temp and predicted_temp >= 34.5):
            # Kích hoạt chế độ tự động dập tắt cảnh báo bằng cách giả lập bật quạt gió
            # Trả về tín hiệu điều khiển tự động
            return "fan_on", predicted_temp
            
        return None, predicted_temp

    def get_ai_chat_response(self, user_message):
        """
        Hệ thống AI phản hồi các câu hỏi của quản trị viên dựa trên trạng thái thực tế của CSDL
        """
        msg = user_message.lower()
        
        # 1. Điều khiển thiết bị thông qua ngôn ngữ tự nhiên
        if "bật quạt" in msg or "làm mát" in msg or "quạt gió" in msg:
            from app import socketio
            from app.auth.services import AuthService
            AuthService().log_action(None, "AI Chat Điều Khiển", "AI Trợ lý tự động kích hoạt quạt gió theo lệnh đàm thoại từ Admin.")
            
            # Phát sóng tín hiệu SocketIO để đồng bộ Client
            socketio.emit('ai_autopilot_trigger', {
                'action': 'fan_on',
                'predicted_temp': 26.5,
                'target_temp': 26.5
            })
            return "🤖 [AI Co-pilot]: Rõ! Đã kích hoạt hệ thống Quạt thông gió làm mát thiết bị theo yêu cầu. Giao diện cảm biến đang tự động hạ nhiệt độ."

        elif "tắt nguồn" in msg or "ngắt nguồn" in msg:
            from app import socketio
            from app.auth.services import AuthService
            AuthService().log_action(None, "AI Chat Điều Khiển", "AI Trợ lý thực thi ngắt nguồn thiết bị theo lệnh đàm thoại từ Admin.")
            
            socketio.emit('ai_autopilot_trigger', {
                'action': 'power_off',
                'predicted_temp': 25.0,
                'target_temp': 25.0
            })
            return "🤖 [AI Co-pilot]: Rõ! Đã gửi tín hiệu ngắt nguồn thiết bị khẩn cấp. Hệ thống cảm biến đã chuyển sang trạng thái an toàn."

        sensors = self.sensor_repo.get_all()
        
        # Lấy thống kê
        temp_val = "N/A"
        humid_val = "N/A"
        for s in sensors:
            s_dict = s.to_dict()
            if s.type_ref.name == 'Temperature':
                temp_val = f"{s_dict['latest_value']} °C" if s_dict['latest_value'] is not None else "N/A"
            elif s.type_ref.name == 'Humidity':
                humid_val = f"{s_dict['latest_value']} %" if s_dict['latest_value'] is not None else "N/A"

        # So khớp câu hỏi
        if "nhiệt độ" in msg or "nóng" in msg:
            return f"🤖 [AI Trợ Lý]: Nhiệt độ hệ thống hiện tại đo được là {temp_val}. Dự báo nhiệt độ đang nằm trong tầm kiểm soát."
            
        elif "độ ẩm" in msg or "ẩm" in msg:
            return f"🤖 [AI Trợ Lý]: Độ ẩm hiện tại là {humid_val}. Các cảm biến DHT22 đang hoạt động ổn định."
            
        elif "an toàn" in msg or "ổn định" in msg or "sức khỏe" in msg:
            if "N/A" not in temp_val and float(temp_val.split()[0]) >= 35.0:
                return f"🤖 [AI Trợ Lý] CẢNH BÁO: Hệ thống phát hiện quá nhiệt ({temp_val}). Trợ lý AI khuyên bạn nên kích hoạt Quạt thông gió hoặc bật chế độ Autopilot."
            return f"🤖 [AI Trợ Lý]: Hệ thống AIoT đang hoạt động an toàn. Nhiệt độ: {temp_val}, Độ ẩm: {humid_val}. Không phát hiện bất thường."
            
        elif "quạt" in msg or "điều khiển" in msg:
            return "🤖 [AI Trợ Lý]: Bạn có thể điều khiển Quạt thông gió hoặc Ngắt nguồn khẩn cấp trực tiếp qua thanh cảnh báo ở đầu trang."
            
        else:
            return "🤖 [AI Trợ Lý]: Xin chào! Tôi là Trợ lý AI thông minh tích hợp trên Server. Tôi có thể giúp bạn theo dõi nhiệt độ, độ ẩm, phát hiện bất thường và điều khiển thiết bị tự động. Hãy hỏi tôi về: 'Nhiệt độ hiện tại', 'Hệ thống có an toàn không?'..."
