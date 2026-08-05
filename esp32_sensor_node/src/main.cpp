#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h> // Để hỗ trợ domain radar.local

// ==========================================
// CÀI ĐẶT WIFI VÀ CHÂN CẮM
// ==========================================
const char* ssid = "Mmm";         // Thay bằng tên WiFi nhà bạn
const char* password = "22222222"; // Thay bằng mật khẩu WiFi

// Chân HC-SR04 kết nối với ESP32-S3
const int trigPin = 5; 
const int echoPin = 6; 

// Khởi tạo WebServer ở port 80
WebServer server(80);

void setup() {
  Serial.begin(115200);

  // Đấu nối mạch điện
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Kết nối Wi-Fi
  Serial.print("Đang kết nối WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nKết nối WiFi thành công!");
  Serial.print("Địa chỉ IP: ");
  Serial.println(WiFi.localIP());

  // Cài đặt tên miền ảo (mDNS)
  if (!MDNS.begin("radar")) {
    Serial.println("Lỗi cấu hình mDNS");
  } else {
    Serial.println("Bạn có thể truy cập mạch qua domain: http://radar.local");
  }

  // TẠO ĐƯỜNG DẪN API TRẢ VỀ KHOẢNG CÁCH
  server.on("/distance", []() {
    // Thêm header CORS để trang Web ở VS Code (Flask) gọi được API này mà không bị chặn
    server.sendHeader("Access-Control-Allow-Origin", "*");
    
    // Phát xung siêu âm
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    // Đo thời gian và tính khoảng cách
    long duration = pulseIn(echoPin, HIGH);
    int distance = duration * 0.034 / 2;
    
    // Trả về số đo
    server.send(200, "text/plain", String(distance));
  });

  server.begin();
  Serial.println("API Server đã sẵn sàng!");
}

void loop() {
  // Lắng nghe yêu cầu HTTP
  server.handleClient();
}
