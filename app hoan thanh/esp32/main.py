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
SSID = "Mmm"
# Mật khẩu Wifi của bạn
PASSWORD = "22222222"

# ==========================================
# CẤU HÌNH IP CỦA MÁY CHỦ FLASK
# ==========================================
SERVER_IP = "10.10.9.224"
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

# Cấu hình chân HC-SR04
TRIG_PIN = 12
ECHO_PIN = 13
trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
trig.off() # Đảm bảo chân Trig ban đầu ở mức LOW
echo = machine.Pin(ECHO_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)

def get_distance():
    # Chờ chân echo về mức LOW nếu bị treo từ lần đo trước
    wait_low_timeout = 2000
    while echo.value() == 1 and wait_low_timeout > 0:
        time.sleep_us(5)
        wait_low_timeout -= 1
        
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    
    try:
        # 1. Chờ chân echo lên HIGH
        t0 = time.ticks_us()
        # Chờ tối đa 10ms (10000us) để phát hiện bắt đầu xung echo
        while echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), t0) > 10000:
                print("HC-SR04 Debug: Echo start timeout")
                return -1.0
                
        t1 = time.ticks_us()
        
        # 2. Đo độ dài xung HIGH (Echo)
        # Chờ tối đa 30ms (30000us) để xung kết thúc (~5m)
        while echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), t1) > 30000:
                print("HC-SR04 Debug: Echo end timeout")
                return -1.0
                
        t2 = time.ticks_us()
        duration = time.ticks_diff(t2, t1)
        
        # Tính khoảng cách (cm)
        distance = duration / 58.0
        return round(distance, 1)
    except Exception as e:
        print("Lỗi đo khoảng cách thủ công:", e)
        return -1.0

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
            headers = {'Content-Type': 'application/json'}

            # 1. ĐỌC CẢM BIẾN DHT11 VÀ GỬI LÊN SERVER
            if sensor:
                try:
                    sensor.measure()
                    t = sensor.temperature()
                    h = sensor.humidity()
                    
                    print(f"DHT11 - Nhiệt độ: {t}°C, Độ ẩm: {h}%")
                    
                    # Gửi Nhiệt độ (Sensor ID 1)
                    try:
                        res = requests.post(f"{BASE_URL}/api/sensors/1/data", data='{"value": ' + str(t) + '}', headers=headers)
                        res.close()
                    except Exception as e:
                        print("Lỗi gửi nhiệt độ:", e)
                        
                    # Gửi Độ ẩm (Sensor ID 2)
                    try:
                        res = requests.post(f"{BASE_URL}/api/sensors/2/data", data='{"value": ' + str(h) + '}', headers=headers)
                        res.close()
                    except Exception as e:
                        print("Lỗi gửi độ ẩm:", e)
                        
                except Exception as e:
                    print("Lỗi đọc cảm biến DHT11 (Chưa cắm chặt hoặc sai chân):", e)
            else:
                print("Chưa khởi tạo được cảm biến DHT11 ở chân GPIO", DHT_PIN)
            
            # 2. ĐỌC CẢM BIẾN KHOẢNG CÁCH HC-SR04 VÀ GỬI LÊN SERVER
            dist = get_distance()
            if dist >= 0:
                print(f"HC-SR04 - Khoảng cách: {dist} cm")
                try:
                    res = requests.post(f"{BASE_URL}/api/sensors/4/data", data='{"value": ' + str(dist) + '}', headers=headers)
                    res.close()
                except Exception as e:
                    print("Lỗi gửi khoảng cách:", e)
            else:
                print("Lỗi đọc cảm biến khoảng cách HC-SR04")

            # 3. HỎI SERVER XEM TRẠNG THÁI LED LÀ GÌ ĐỂ BẬT/TẮT
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
