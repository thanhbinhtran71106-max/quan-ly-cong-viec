#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

// ---------------------------------------------------------
// THIẾT LẬP MẠNG WI-FI (Vui lòng thay đổi thông tin này)
// ---------------------------------------------------------
const char* ssid = "tranthanhbinh";         // Tên Wi-Fi của bạn
const char* password = "mk71106"; // Mật khẩu Wi-Fi của bạn

WebServer server(80);
Preferences preferences;

// ---------------------------------------------------------
// CẤU HÌNH THIẾT BỊ ĐỘNG
// ---------------------------------------------------------
struct Device {
  int id;
  String name;
  int pin;
  int state;
};

const int MAX_DEVICES = 20;
Device devices[MAX_DEVICES];
int deviceCount = 0;

const int maxLogs = 10;
String activityLogs[maxLogs];
int logCount = 0;

void saveConfig() {
  preferences.clear();
  preferences.putInt("devCount", deviceCount);
  for (int i=0; i<deviceCount; i++) {
    preferences.putInt(("id"+String(i)).c_str(), devices[i].id);
    preferences.putString(("name"+String(i)).c_str(), devices[i].name);
    preferences.putInt(("pin"+String(i)).c_str(), devices[i].pin);
    preferences.putInt(("state"+String(i)).c_str(), devices[i].state);
  }
}

void loadConfig() {
  preferences.begin("aiot", false);
  deviceCount = preferences.getInt("devCount", 0);
  
  if (deviceCount == 0) {
    // Mặc định 8 LED nếu chưa có cấu hình
    deviceCount = 8;
    int defaultPins[] = {4, 5, 6, 7, 15, 16, 17, 18};
    for (int i=0; i<8; i++) {
      devices[i].id = i;
      devices[i].name = "LED " + String(i+1);
      devices[i].pin = defaultPins[i];
      devices[i].state = 0;
    }
    saveConfig();
  } else {
    for (int i=0; i<deviceCount; i++) {
      devices[i].id = preferences.getInt(("id"+String(i)).c_str(), i);
      devices[i].name = preferences.getString(("name"+String(i)).c_str(), "Unknown");
      devices[i].pin = preferences.getInt(("pin"+String(i)).c_str(), 0);
      devices[i].state = preferences.getInt(("state"+String(i)).c_str(), 0);
    }
  }
  
  // Khởi tạo GPIO
  for(int i=0; i<deviceCount; i++){
    pinMode(devices[i].pin, OUTPUT);
    digitalWrite(devices[i].pin, devices[i].state == 1 ? HIGH : LOW);
  }
}

// ---------------------------------------------------------
// GIAO DIỆN WEB (HTML, CSS, JS) - Được lưu trữ trong ESP32
// ---------------------------------------------------------
const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
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
    <div class="loading" id="loader"></div>
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
</html>
)rawliteral";

// ---------------------------------------------------------
// XỬ LÝ CÁC YÊU CẦU (REQUEST) TỪ TRÌNH DUYỆT
// ---------------------------------------------------------

void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void handleGetDevices() {
  String json = "[";
  for(int i=0; i<deviceCount; i++){
    json += "{\"id\":" + String(devices[i].id) + ",\"name\":\"" + devices[i].name + "\",\"pin\":" + String(devices[i].pin) + ",\"state\":" + String(devices[i].state) + "}";
    if(i < deviceCount-1) json += ",";
  }
  json += "]";
  server.send(200, "application/json", json);
}

void handleLedToggle() {
  if (server.hasArg("id") && server.hasArg("state")) {
    int id = server.arg("id").toInt();
    int state = server.arg("state").toInt();
    
    bool found = false;
    for (int i=0; i<deviceCount; i++) {
      if (devices[i].id == id) {
        devices[i].state = state;
        digitalWrite(devices[i].pin, state == 1 ? HIGH : LOW);
        saveConfig();
        found = true;
        break;
      }
    }
    
    if (found) {
      if (server.hasArg("log")) {
        String logStr = server.arg("log");
        if (logCount < maxLogs) {
          for (int i = logCount; i > 0; i--) activityLogs[i] = activityLogs[i-1];
          activityLogs[0] = logStr;
          logCount++;
        } else {
          for (int i = maxLogs - 1; i > 0; i--) activityLogs[i] = activityLogs[i-1];
          activityLogs[0] = logStr;
        }
      }
      server.send(200, "text/plain", "OK");
    } else {
      server.send(400, "text/plain", "Device not found");
    }
  } else {
    server.send(400, "text/plain", "Missing args");
  }
}

void handleAddDevice() {
  if (server.hasArg("name") && server.hasArg("pin")) {
    if (deviceCount >= MAX_DEVICES) {
      server.send(400, "text/plain", "Đã đạt số lượng thiết bị tối đa");
      return;
    }
    String name = server.arg("name");
    int pin = server.arg("pin").toInt();
    
    int newId = millis(); // Tạo ID dựa trên thời gian
    
    devices[deviceCount].id = newId;
    devices[deviceCount].name = name;
    devices[deviceCount].pin = pin;
    devices[deviceCount].state = 0;
    
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    
    deviceCount++;
    saveConfig();
    
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Missing args");
  }
}

void handleRemoveDevice() {
  if (server.hasArg("id")) {
    int id = server.arg("id").toInt();
    bool found = false;
    
    for (int i=0; i<deviceCount; i++) {
      if (devices[i].id == id) {
        found = true;
        // Shift remaining items left
        for (int j = i; j < deviceCount - 1; j++) {
          devices[j] = devices[j+1];
        }
        deviceCount--;
        saveConfig();
        break;
      }
    }
    
    if (found) server.send(200, "text/plain", "OK");
    else server.send(400, "text/plain", "Device not found");
  } else {
    server.send(400, "text/plain", "Missing args");
  }
}

void handleLogs() {
  String json = "[";
  for (int i = 0; i < logCount; i++) {
    json += "\"" + activityLogs[i] + "\"";
    if (i < logCount - 1) json += ",";
  }
  json += "]";
  server.send(200, "application/json", json);
}

// ---------------------------------------------------------
// HÀM SETUP VÀ LOOP CHÍNH
// ---------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(10);
  
  // 1. Tải cấu hình và khởi tạo các chân GPIO
  loadConfig();

  // 2. Kết nối vào mạng Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("");
  Serial.print("Đang kết nối Wi-Fi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("Đã kết nối Wi-Fi thành công!");
  Serial.print("Mở trình duyệt và truy cập IP này để điều khiển: ");
  Serial.println(WiFi.localIP());

  // 3. Đăng ký các hàm xử lý cho Web Server
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/devices", HTTP_GET, handleGetDevices);
  server.on("/api/led", HTTP_GET, handleLedToggle);
  server.on("/api/device/add", HTTP_GET, handleAddDevice);
  server.on("/api/device/remove", HTTP_GET, handleRemoveDevice);
  server.on("/api/logs", HTTP_GET, handleLogs);

  // 4. Khởi động Web Server
  server.begin();
  Serial.println("HTTP server đã khởi động");
}

void loop() {
  // Lắng nghe và xử lý các yêu cầu liên tục
  server.handleClient();
}
