import network
import time
import machine
import dht
import random
try:
    import urequests as requests
except ImportError:
    import requests

# ==========================================
# CẤU HÌNH WI-FI (ĐIỀN CHÍNH XÁC VỚI MẠCH)
# ==========================================
SSID = "MT"
# Mật khẩu Wifi của bạn
PASSWORD = "12345678"

# ==========================================
# CẤU HÌNH IP CỦA MÁY CHỦ FLASK
# ==========================================
SERVER_IP = "172.20.10.7"
SERVER_PORT = "5000"
BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# ==========================================
# CẤU HÌNH PHẦN CỨNG (8 ĐÈN LED)
# ==========================================
# Nếu thiết bị của bạn là Active-Low (ghi 0 thì SÁNG, ghi 1 thì TẮT), hãy để True.
# Nếu là Active-High (ghi 1 thì SÁNG, ghi 0 thì TẮT), hãy sửa lại thành False.
ACTIVE_LOW = True

LED_PINS = [4, 5, 6, 7, 15, 16, 17, 18]
leds = {}
for pin in LED_PINS:
    leds[pin] = machine.Pin(pin, machine.Pin.OUT)
    leds[pin].value(1 if ACTIVE_LOW else 0)

# Cảm biến DHT11 cắm vào chân GPIO 14
DHT_PIN = 14
try:
    sensor = dht.DHT11(machine.Pin(DHT_PIN))
except Exception as e:
    print("Lỗi khởi tạo DHT11:", e)
    sensor = None

# ==========================================
# HÀM KẾT NỐI WI-FI
# ==========================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)
    if not wlan.isconnected():
        print(f"Đang kết nối vào mạng {SSID}...")
        wlan.connect(SSID, PASSWORD)
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            print(".", end="")
            timeout -= 1
            
    if wlan.isconnected():
        print("\nĐã kết nối Wi-Fi thành công!")
        print("Địa chỉ IP của ESP32:", wlan.ifconfig()[0])
        return True
    else:
        print("\nKhông thể kết nối Wi-Fi! Kiểm tra lại Tên, Mật khẩu hoặc Băng tần.")
        return False

# ==========================================
# VÒNG LẶP CHÍNH CỦA HỆ THỐNG AIoT
# ==========================================
def run_system():
    if not connect_wifi():
        print("Dừng hệ thống do không có kết nối mạng.")
        return
        
    print(f"Bắt đầu giao tiếp với AIoT Server tại {BASE_URL}")
    
    while True:
        try:
            # 1. ĐỌC CẢM BIẾN VÀ GỬI LÊN SERVER
            if sensor:
                try:
                    sensor.measure()
                    t = sensor.temperature()
                    h = sensor.humidity()
                    
                    print(f"Nhiệt độ THẬT: {t}°C, Độ ẩm THẬT: {h}%")
                    
                    # Gọi POST API gửi dữ liệu
                    payload = '{"temperature": ' + str(t) + ', "humidity": ' + str(h) + '}'
                    headers = {'Content-Type': 'application/json'}
                    
                    post_url = f"{BASE_URL}/api/sensor"
                    try:
                        res = requests.post(post_url, data=payload, headers=headers)
                        res.close()
                        print("-> Đã gửi dữ liệu cảm biến lên Server")
                    except Exception as e:
                        print("-> Lỗi kết nối HTTP POST:", e)
                        
                except Exception as e:
                    print("Lỗi đọc cảm biến DHT11 (Chưa cắm chặt hoặc sai chân):", e)
            else:
                print("Chưa khởi tạo được cảm biến DHT11 ở chân GPIO", DHT_PIN)
            
            # 2. HỎI SERVER XEM TRẠNG THÁI LED LÀ GÌ ĐỂ BẬT/TẮT
            get_url = f"{BASE_URL}/api/led"
            try:
                res = requests.get(get_url)
                data = res.json()
                res.close()
                
                # Cập nhật cả 8 đèn LED (Có xử lý đảo logic Active-Low)
                for pin in LED_PINS:
                    state = data.get(str(pin), data.get(f"led_{pin}", 0))
                    leds[pin].value(1 - state if ACTIVE_LOW else state)
                print(f"<- Đã đồng bộ trạng thái 8 LED từ Server")
            except Exception as e:
                print("<- Lỗi lấy trạng thái LED:", e)
                
        except Exception as e:
            print("Lỗi hệ thống:", e)
            
        # Đợi 5 giây trước chu kỳ tiếp theo
        print("Đang đợi 5 giây...\n")
        time.sleep(5)

if __name__ == '__main__':
    run_system()
