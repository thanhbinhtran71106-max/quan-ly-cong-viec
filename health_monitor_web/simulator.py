import asyncio
import websockets
import json
import random
import math

async def simulate_esp32_data():
    uri = "ws://localhost:8000/ws"
    
    # Kết nối tới WebSocket server
    try:
        async with websockets.connect(uri) as websocket:
            print("Đã kết nối tới Server. Đang bắt đầu gửi dữ liệu giả lập...")
            
            t = 0
            while True:
                # 1. Giả lập tín hiệu ECG (Sóng P-Q-R-S-T đơn giản hoặc sóng sin kết hợp)
                # Dùng một hàm toán học đơn giản để tạo ra sóng có đỉnh R cao
                base_ecg = 2000
                noise = random.randint(-50, 50)
                
                # Sóng tim cơ bản đập mỗi ~800ms
                heart_phase = t % 40
                if heart_phase == 0:
                    # Đỉnh R
                    ecg_val = base_ecg + 1500 + noise
                elif heart_phase == 1:
                    # Sóng S
                    ecg_val = base_ecg - 500 + noise
                elif heart_phase == 5 or heart_phase == 6:
                    # Sóng T
                    ecg_val = base_ecg + 300 + noise
                elif heart_phase == 35:
                    # Sóng P
                    ecg_val = base_ecg + 150 + noise
                else:
                    # Baseline
                    ecg_val = base_ecg + noise
                
                # 2. Giả lập các thông số sinh tồn khác (cập nhật chậm hơn)
                # Dữ liệu tĩnh hơn, chỉ hơi nhiễu nhẹ
                bpm = 75 + random.randint(-2, 2)
                spo2 = 98 + random.choice([0, 0, 0, -1, 1])
                body_temp = 36.5 + random.uniform(-0.1, 0.2)
                room_temp = 25.0 + random.uniform(-0.1, 0.1)
                humidity = 55.0 + random.uniform(-1.0, 1.0)
                
                # Đóng gói dữ liệu
                payload = {
                    "ecg": ecg_val,
                    "bpm": bpm,
                    "spo2": spo2,
                    "body_temp": body_temp,
                    "room_temp": room_temp,
                    "humidity": humidity
                }
                
                # Gửi lên server
                await websocket.send(json.dumps(payload))
                
                t += 1
                # Gửi với tốc độ 50Hz (20ms) để giống tốc độ lấy mẫu ECG
                await asyncio.sleep(0.02)
                
    except Exception as e:
        print(f"Không thể kết nối hoặc lỗi: {e}")
        print("Hãy chắc chắn server Uvicorn đang chạy!")

if __name__ == "__main__":
    asyncio.run(simulate_esp32_data())
