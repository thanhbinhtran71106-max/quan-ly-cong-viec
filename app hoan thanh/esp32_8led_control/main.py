import network
import socket
import machine
import time
import json
import os

# ==========================================
SSID = "Mmm"
PASSWORD = "22222222"
# ==========================================

# ==========================================
# CẤU HÌNH THIẾT BỊ
# ==========================================
devices_config = []
devices_pins = {}
activity_logs = []

def load_config():
    global devices_config
    try:
        with open('devices.json', 'r') as f:
            devices_config = json.loads(f.read())
    except:
        # Mặc định 8 LED nếu chưa có file
        devices_config = [
            {"id": i, "name": f"LED {i+1}", "pin": p, "state": 0}
            for i, p in enumerate([4, 5, 6, 7, 15, 16, 17, 18])
        ]
        save_config()
        
    for d in devices_config:
        try:
            pin = machine.Pin(d['pin'], machine.Pin.OUT)
            pin.value(d['state'])
            devices_pins[d['id']] = pin
        except Exception as e:
            print("Error init pin", d['pin'], e)

def save_config():
    try:
        with open('devices.json', 'w') as f:
            f.write(json.dumps(devices_config))
    except Exception as e:
        print("Error saving config:", e)

load_config()

# ==========================================
# GIAO DIỆN WEB (HTML, CSS, JS)
# ==========================================
def get_html():
    return """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 AIOT COMMAND CENTER</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: #fff; min-height: 100vh; padding: 2rem; }
        h1 { font-size: 2.2rem; margin-bottom: 2rem; text-align: center; color: #00f2fe; text-shadow: 0 4px 15px rgba(0,242,254,0.3); }
        .dashboard { display: flex; flex-wrap: wrap; gap: 2rem; max-width: 1200px; margin: 0 auto; width: 100%; align-items: flex-start; }
        .sidebar { flex: 1 1 300px; display: flex; flex-direction: column; gap: 1.5rem; }
        .main-content { flex: 3 1 600px; }
        .user-info { font-size: 1.2rem; color: #00C9FF; font-weight: 600; text-align: center; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 10px; }
        .toolbar { display: flex; justify-content: center; }
        .btn-add { background: #00C9FF; color: #000; border: none; padding: 15px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 100%; font-size: 1.1rem; }
        .btn-add:hover { background: #92FE9D; box-shadow: 0 0 15px rgba(146, 254, 157, 0.4); }
        .container { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1.5rem; width: 100%; }
        .card { position: relative; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 2rem 1rem; display: flex; flex-direction: column; align-items: center; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); transition: transform 0.3s ease; }
        .card:hover { transform: translateY(-5px); border-color: rgba(255, 255, 255, 0.2); }
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; color: #e0e0e0; }
        .card-pin { font-size: 0.8rem; color: #aaa; margin-bottom: 1rem; }
        .btn-remove { position: absolute; top: 10px; right: 10px; background: rgba(255,0,0,0.2); color: #ff4c4c; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; }
        .btn-remove:hover { background: #ff4c4c; color: #fff; }
        .switch { position: relative; display: inline-block; width: 60px; height: 34px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; transition: .4s; border-radius: 34px; }
        .slider:before { position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); }
        input:checked + .slider:before { transform: translateX(26px); }
        .status { margin-top: 1rem; font-size: 0.9rem; color: #888; font-weight: 600; }
        .status.on { color: #92FE9D; text-shadow: 0 0 10px rgba(146, 254, 157, 0.5); }
        .log-container { background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 10px; max-height: 500px; display: flex; flex-direction: column; }
        .log-container h3 { font-size: 1.1rem; color: #e0e0e0; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; }
        .log-item { padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem; color: #ccc; }
        .log-item:last-child { border-bottom: none; }
        #logs { overflow-y: auto; flex-grow: 1; }
        
        /* Modal */
        .modal { display: none; position: fixed; z-index: 100; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); align-items: center; justify-content: center; }
        .modal-content { background: #1e293b; padding: 2rem; border-radius: 15px; width: 300px; text-align: center; }
        .modal-content h2 { margin-bottom: 1rem; font-size: 1.3rem; }
        .modal-content input { width: 100%; padding: 10px; margin-bottom: 1rem; border-radius: 5px; border: 1px solid #334155; background: #0f172a; color: #fff; }
        .modal-buttons { display: flex; justify-content: space-between; }
        .btn-save { background: #00C9FF; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; color: #000; font-weight: bold; }
        .btn-cancel { background: #475569; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; color: #fff; }
    </style>
</head>
<body>
    <h1>AIOT COMMAND CENTER</h1>
    <div class="dashboard">
        <!-- Cột bên trái: Công cụ và Lịch sử -->
        <div class="sidebar">
            <div class="user-info" id="user-info"></div>
            
            <div class="toolbar">
                <button class="btn-add" onclick="document.getElementById('addModal').style.display='flex'">+ Thêm Thiết Bị</button>
            </div>
            
            <div class="log-container" id="log-container">
                <h3>Lịch sử hoạt động</h3>
                <div id="logs">Chưa có hoạt động nào.</div>
            </div>
        </div>
        
        <!-- Cột bên phải: Các thiết bị -->
        <div class="main-content">
            <div class="container" id="device-container"></div>
        </div>
    </div>

    <!-- Modal Thêm Thiết Bị -->
    <div id="addModal" class="modal">
        <div class="modal-content">
            <h2>Thêm Thiết Bị Mới</h2>
            <input type="text" id="devName" placeholder="Tên thiết bị (VD: Quạt)">
            <input type="number" id="devPin" placeholder="Chân GPIO (VD: 19)">
            <div class="modal-buttons">
                <button class="btn-cancel" onclick="document.getElementById('addModal').style.display='none'">Hủy</button>
                <button class="btn-save" onclick="addDevice()">Lưu</button>
            </div>
        </div>
    </div>

    <script>
        let userName = localStorage.getItem('esp_user_name');
        if (!userName) {
            userName = prompt('Vui lòng nhập tên của bạn:');
            if (!userName || userName.trim() === '') userName = 'Khách';
            localStorage.setItem('esp_user_name', userName);
        }
        document.getElementById('user-info').innerText = 'Xin chào, ' + userName;

        const container = document.getElementById('device-container');
        let devices = [];

        function renderDevices() {
            container.innerHTML = '';
            devices.forEach(dev => {
                container.innerHTML += `
                    <div class="card" id="card-${dev.id}">
                        <button class="btn-remove" onclick="removeDevice(${dev.id})">✕</button>
                        <div class="card-title">${dev.name}</div>
                        <div class="card-pin">GPIO ${dev.pin}</div>
                        <label class="switch">
                            <input type="checkbox" id="dev-${dev.id}" ${dev.state ? 'checked' : ''} onchange="toggleDevice(${dev.id}, this)">
                            <span class="slider"></span>
                        </label>
                        <div class="status ${dev.state ? 'on' : ''}" id="status-${dev.id}">${dev.state ? 'BẬT' : 'TẮT'}</div>
                    </div>`;
            });
        }

        function loadDevices() {
            fetch('/api/devices').then(r => r.json()).then(data => {
                devices = data;
                renderDevices();
            }).catch(e => console.error(e));
        }

        function toggleDevice(id, element) {
            const state = element.checked ? 1 : 0;
            const dev = devices.find(d => d.id === id);
            const devName = dev ? dev.name : ('Device ' + id);
            
            document.getElementById(`status-${id}`).textContent = state ? 'BẬT' : 'TẮT';
            document.getElementById(`status-${id}`).classList.toggle('on', state);
            
            const time = new Date().toLocaleTimeString('vi-VN');
            const action = state ? 'BẬT' : 'TẮT';
            const logMsg = `[${time}] ${userName} đã ${action} ${devName}`;
            
            fetch(`/api/led?id=${id}&state=${state}&log=${encodeURIComponent(logMsg)}`).catch(() => alert("Lỗi kết nối tới ESP32!"));
        }
        
        function addDevice() {
            const name = document.getElementById('devName').value;
            const pin = document.getElementById('devPin').value;
            if(!name || !pin) { alert("Vui lòng nhập đủ thông tin!"); return; }
            
            fetch(`/api/device/add?name=${encodeURIComponent(name)}&pin=${pin}`)
                .then(r => r.text())
                .then(msg => {
                    if(msg === "OK") {
                        document.getElementById('addModal').style.display='none';
                        document.getElementById('devName').value = '';
                        document.getElementById('devPin').value = '';
                        loadDevices();
                    } else {
                        alert(msg);
                    }
                }).catch(e => alert("Lỗi kết nối!"));
        }

        function removeDevice(id) {
            if(!confirm("Bạn có chắc muốn xoá thiết bị này?")) return;
            fetch(`/api/device/remove?id=${id}`)
                .then(r => r.text())
                .then(msg => {
                    if(msg === "OK") loadDevices();
                    else alert(msg);
                }).catch(e => alert("Lỗi kết nối!"));
        }

        function loadLogs() {
            fetch('/api/logs').then(r => r.json()).then(data => {
                const logsDiv = document.getElementById('logs');
                if (data.length === 0) {
                    logsDiv.innerHTML = 'Chưa có hoạt động nào.';
                } else {
                    logsDiv.innerHTML = '';
                    data.forEach(log => {
                        logsDiv.innerHTML += `<div class="log-item">${decodeURIComponent(log)}</div>`;
                    });
                }
            }).catch(e => console.error(e));
        }
        
        setInterval(loadLogs, 2000);
        
        window.onload = () => {
            loadDevices();
            loadLogs();
        };
    </script>
</body>
</html>"""

# ==========================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)
    if not wlan.isconnected():
        print("Đang kết nối Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        print("Đã kết nối Wi-Fi thành công!")
        print("Địa chỉ IP:", wlan.ifconfig()[0])
        return wlan.ifconfig()[0]
    return None

def url_decode(s):
    res = ""
    i = 0
    while i < len(s):
        if s[i] == '%':
            try:
                res += chr(int(s[i+1:i+3], 16))
                i += 3
            except:
                res += '%'
                i += 1
        elif s[i] == '+':
            res += ' '
            i += 1
        else:
            res += s[i]
            i += 1
    return res

def start_server():
    global devices_config
    ip = connect_wifi()
    if not ip: return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    print("HTTP server đang chạy.")

    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024)
            if not request:
                conn.close()
                continue
                
            request_str = request.decode('utf-8')
            request_line = request_str.split('\r\n')[0]
            
            if "/api/devices" in request_line:
                json_data = json.dumps(devices_config)
                response = 'HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n\n' + json_data
                conn.send(response.encode('utf-8'))
                
            elif "/api/led" in request_line:
                parts = request_line.split(' ')[1]
                if '?' in parts:
                    params = parts.split('?')[1].split('&')
                    id_val = None
                    state_val = None
                    log_val = None
                    for p in params:
                        if p.startswith('id='): id_val = int(p.split('=')[1])
                        if p.startswith('state='): state_val = int(p.split('=')[1])
                        if p.startswith('log='): log_val = p.split('=', 1)[1]
                    
                    if id_val is not None and state_val is not None:
                        for d in devices_config:
                            if d['id'] == id_val:
                                d['state'] = state_val
                                if id_val in devices_pins:
                                    devices_pins[id_val].value(state_val)
                                save_config()
                                break
                        if log_val:
                            activity_logs.insert(0, log_val)
                            if len(activity_logs) > 10: activity_logs.pop()
                            
                conn.send('HTTP/1.1 200 OK\nContent-Type: text/plain\nConnection: close\n\nOK'.encode('utf-8'))
                
            elif "/api/device/add" in request_line:
                parts = request_line.split(' ')[1]
                msg = "OK"
                if '?' in parts:
                    params = parts.split('?')[1].split('&')
                    name = "New Device"
                    pin = -1
                    for p in params:
                        if p.startswith('name='): name = url_decode(p.split('=', 1)[1])
                        if p.startswith('pin='): pin = int(p.split('=')[1])
                    
                    if pin >= 0:
                        new_id = int(time.time()) if hasattr(time, 'time') else len(devices_config) + 100
                        while any(d['id'] == new_id for d in devices_config): new_id += 1
                        
                        devices_config.append({"id": new_id, "name": name, "pin": pin, "state": 0})
                        try:
                            devices_pins[new_id] = machine.Pin(pin, machine.Pin.OUT)
                            devices_pins[new_id].value(0)
                        except Exception as e:
                            msg = "Lỗi khởi tạo GPIO: " + str(e)
                        save_config()
                    else: msg = "Invalid pin"
                conn.send(('HTTP/1.1 200 OK\nContent-Type: text/plain\nConnection: close\n\n' + msg).encode('utf-8'))

            elif "/api/device/remove" in request_line:
                parts = request_line.split(' ')[1]
                if '?' in parts:
                    params = parts.split('?')[1].split('&')
                    remove_id = None
                    for p in params:
                        if p.startswith('id='): remove_id = int(p.split('=')[1])
                    
                    if remove_id is not None:
                        devices_config = [d for d in devices_config if d['id'] != remove_id]
                        if remove_id in devices_pins:
                            del devices_pins[remove_id]
                        save_config()
                conn.send('HTTP/1.1 200 OK\nContent-Type: text/plain\nConnection: close\n\nOK'.encode('utf-8'))

            elif "/api/logs" in request_line:
                json_data = json.dumps(activity_logs)
                response = 'HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n\n' + json_data
                conn.send(response.encode('utf-8'))
                
            else:
                response = 'HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n' + get_html()
                conn.send(response.encode('utf-8'))
                
            conn.close()
        except Exception as e:
            print("Lỗi kết nối:", e)
            try: conn.close()
            except: pass

if __name__ == "__main__":
    start_server()
