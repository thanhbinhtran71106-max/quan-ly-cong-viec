import serial
import time
import re

print("Opening COM4...")
try:
    ser = serial.Serial('COM4', 115200, timeout=1)
    # Reset mạch bằng DTR/RTS
    ser.setDTR(False)
    ser.setRTS(False)
    time.sleep(0.1)
    ser.setDTR(True)
    ser.setRTS(True)
    time.sleep(0.1)
    ser.setDTR(False)
    ser.setRTS(False)
    
    print("Waiting for ESP32 to boot and connect to Wi-Fi...")
    start_time = time.time()
    ip_address = None
    
    while time.time() - start_time < 15:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print("[ESP32]", line)
            # Tìm dòng chữ có chứa IP (vd: 192.168.1.45)
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
            if match and "0.0.0.0" not in line:
                ip_address = match.group(1)
                break
    
    if ip_address:
        print("\n\n>>> FOUND ESP32 IP:", ip_address)
        # Tự động cập nhật file esp32.py
        with open('../esp32.py', 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'self.esp_ip = ".*?"', f'self.esp_ip = "{ip_address}"', content)
        with open('../esp32.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print(">>> AUTO-UPDATED esp32.py!")
    else:
        print("\n>>> IP NOT FOUND (Check Wi-Fi password or signal)")
    
    ser.close()
except Exception as e:
    print("ERROR:", e)
