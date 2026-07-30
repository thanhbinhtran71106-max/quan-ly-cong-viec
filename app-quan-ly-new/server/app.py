import sqlite3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import datetime

app = Flask(__name__)
app.secret_key = 'aiot_super_secret_key_pro_max'
DB_NAME = 'aiot.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tạo bảng dữ liệu cảm biến (Nhiệt độ, Độ ẩm, Ánh sáng, AI)
    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            light REAL,
            ai_status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Thêm cột mới nếu bảng cũ chưa có
    for col in ['ai_status', 'light']:
        try:
            c.execute(f"ALTER TABLE sensor_data ADD COLUMN {col} {'REAL' if col == 'light' else 'TEXT'}")
        except Exception:
            pass

    # Bảng nhật ký hoạt động
    c.execute('''
        CREATE TABLE IF NOT EXISTS device_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bảng trạng thái thiết bị
    c.execute('''
        CREATE TABLE IF NOT EXISTS device_state (
            device_id TEXT PRIMARY KEY,
            led_state INTEGER
        )
    ''')
    
    # Bảng User (admin, technician, user)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Tạo sẵn tài khoản admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    
    # Tạo sẵn tài khoản kỹ thuật viên
    c.execute("SELECT * FROM users WHERE username='kythuatvien'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES ('kythuatvien', 'kt123', 'technician')")
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except:
        pass
    
    # Bảng Thiết bị
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE,
            device_name TEXT,
            username TEXT,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    try:
        c.execute("ALTER TABLE devices ADD COLUMN username TEXT")
    except:
        pass
    
    c.execute("INSERT OR IGNORE INTO devices (device_id, device_name, username) VALUES ('esp32', 'ESP32 Phong Khach', 'admin')")
    
    # Bảng Support Tickets
    c.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            is_paid INTEGER DEFAULT 1,
            dev_reply TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bảng User Logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bảng Quy tắc tự động hóa (Auto Rules)
    c.execute('''
        CREATE TABLE IF NOT EXISTS auto_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            sensor_type TEXT,
            condition TEXT,
            threshold REAL,
            action_type TEXT,
            action_value INTEGER,
            is_active INTEGER DEFAULT 1,
            created_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        c.execute("ALTER TABLE auto_rules ADD COLUMN pin_target INTEGER DEFAULT 4")
    except Exception:
        pass
    
    # Bảng Thông báo (Notifications)
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            username TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Thêm quy tắc mẫu nếu chưa có
    c.execute("SELECT COUNT(*) FROM auto_rules")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO auto_rules (rule_name, sensor_type, condition, threshold, action_type, action_value, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("Quat lam mat", "temperature", ">", 35, "led", 1, "admin"))
        c.execute("INSERT INTO auto_rules (rule_name, sensor_type, condition, threshold, action_type, action_value, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("Bat den khi toi", "light", "<", 20, "led", 1, "admin"))
    
    c.execute("INSERT OR IGNORE INTO device_state (device_id, led_state) VALUES ('esp32', 0)")
    for pin in [4, 5, 6, 7, 15, 16, 17, 18]:
        c.execute("INSERT OR IGNORE INTO device_state (device_id, led_state) VALUES (?, 0)", (f"led_{pin}",))
    c.execute("INSERT OR IGNORE INTO device_state (device_id, led_state) VALUES ('sensor_auto', 1)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Giao diện đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user[3]
            
            c = sqlite3.connect(DB_NAME).cursor()
            c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, "Dang nhap he thong"))
            c.connection.commit()
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Sai tai khoan hoac mat khau!")
            
    return render_template('login.html')

# Giao diện Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
            c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, "Dang ky tai khoan moi"))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error="Ten tai khoan da ton tai!")
            
    return render_template('register.html')

# Đăng xuất
@app.route('/logout')
def logout():
    if 'username' in session:
        c = sqlite3.connect(DB_NAME).cursor()
        c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (session['username'], "Dang xuat"))
        c.connection.commit()
        
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# AI Logic: Phân tích bất thường (Nhiệt độ + Độ ẩm + Ánh sáng)
def analyze_anomaly(temp, hum, light=None):
    alerts = []
    recs = []
    
    if temp > 35:
        alerts.append(f"NHIET DO CAO ({temp}C)")
        recs.append("Hay bat quat lam mat ngay lap tuc.")
    elif temp < 15:
        alerts.append(f"NHIET DO THAP ({temp}C)")
        recs.append("Nen kich hoat lo suoi.")
        
    if hum > 85:
        alerts.append(f"DO AM CAO ({hum}%)")
        recs.append("Nen mo may hut am khong khi.")
    elif hum < 30:
        alerts.append(f"DO AM THAP ({hum}%)")
        recs.append("Hay bat may phun suong tao am.")
    
    if light is not None:
        if light < 20:
            alerts.append(f"ANH SANG YEU ({light}%)")
            recs.append("Nen bat den chieu sang.")
        elif light > 90:
            alerts.append(f"ANH SANG QUA MANH ({light}%)")
            recs.append("Nen keo rem che nang.")
        
    if alerts:
        alert_str = "BAT THUONG: " + " & ".join(alerts)
        rec_str = "DE XUAT: " + " ".join(recs)
        return alert_str + " | " + rec_str
    return "Binh thuong"

# Kiểm tra và thực thi quy tắc tự động
def check_auto_rules(temp, hum, light):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Kiểm tra xem chế độ cảm biến tự động có đang bật không
    c.execute("SELECT led_state FROM device_state WHERE device_id = 'sensor_auto'")
    row = c.fetchone()
    if not row or row[0] == 0:
        conn.close()
        return
        
    c.execute("SELECT id, rule_name, sensor_type, condition, threshold, action_type, action_value, is_active, created_by, timestamp, pin_target FROM auto_rules WHERE is_active = 1")
    rules = c.fetchall()
    
    for rule in rules:
        rule_id, rule_name, sensor_type, condition, threshold, action_type, action_value, is_active, created_by, ts, pin_target = rule
        
        sensor_val = None
        if sensor_type == 'temperature':
            sensor_val = temp
        elif sensor_type == 'humidity':
            sensor_val = hum
        elif sensor_type == 'light' and light is not None:
            sensor_val = light
        
        if sensor_val is None:
            continue
            
        triggered = False
        if condition == '>' and sensor_val > threshold:
            triggered = True
        elif condition == '<' and sensor_val < threshold:
            triggered = True
        elif condition == '>=' and sensor_val >= threshold:
            triggered = True
        elif condition == '<=' and sensor_val <= threshold:
            triggered = True
        elif condition == '==' and sensor_val == threshold:
            triggered = True
        
        if triggered and action_type == 'led':
            pin = pin_target if pin_target is not None else 4
            c.execute("UPDATE device_state SET led_state = ? WHERE device_id = ?", (action_value, f"led_{pin}"))
            action_text = "BAT" if action_value == 1 else "TAT"
            c.execute("INSERT INTO device_logs (action) VALUES (?)", 
                      (f"TU DONG {action_text} LED {pin} (Rule: {rule_name})",))
            # Thông báo
            c.execute("INSERT INTO notifications (title, message, type, username) VALUES (?, ?, ?, ?)",
                      (f"Tu dong hoa kich hoat",
                       f"Quy tac '{rule_name}' da {action_text} LED {pin} (Gia tri: {sensor_val})",
                       "warning", "admin"))
    
    conn.commit()
    conn.close()

# API Hỗ trợ trả phí (Tickets)
@app.route('/api/support', methods=['GET', 'POST'])
def manage_support():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message')
        is_paid = data.get('is_paid', 1)
        
        if message:
            c.execute("INSERT INTO support_tickets (username, message, is_paid) VALUES (?, ?, ?)", 
                      (session['username'], message, is_paid))
            c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", 
                      (session['username'], f"Gui yeu cau ho tro: {message[:20]}..."))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "msg": "Da gui yeu cau!"}), 200
        return jsonify({"error": "Thieu noi dung"}), 400
        
    c.execute("SELECT id, message, dev_reply, timestamp FROM support_tickets WHERE username=? ORDER BY timestamp DESC", (session['username'],))
    rows = c.fetchall()
    conn.close()
    
    tickets = [{"id": r[0], "message": r[1], "reply": r[2], "timestamp": r[3]} for r in rows]
    return jsonify(tickets), 200

# API Ping thiết bị
@app.route('/api/ping', methods=['POST'])
def ping_device():
    data = request.get_json()
    device_id = data.get('device_id', 'esp32')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE devices SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?", (device_id,))
    if c.rowcount == 0:
        c.execute("INSERT INTO devices (device_id, device_name) VALUES (?, ?)", (device_id, f"Device {device_id}"))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"}), 200

# API Thiết bị
@app.route('/api/devices', methods=['GET', 'POST'])
def manage_devices():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        
        if not device_id or not device_name:
            conn.close()
            return jsonify({"status": "error", "message": "Thieu thong tin"}), 400
            
        try:
            c.execute("INSERT INTO devices (device_id, device_name, username) VALUES (?, ?, ?)", 
                      (device_id, device_name, session['username']))
            c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", 
                      (session['username'], f"Them thiet bi moi: {device_name} ({device_id})"))
            conn.commit()
            conn.close()
            return jsonify({"status": "success"}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"status": "error", "message": "Thiet bi da ton tai"}), 400

    if session.get('role') in ['admin', 'technician']:
        c.execute("SELECT device_id, device_name, (strftime('%s','now') - strftime('%s', last_seen)) as sec_diff FROM devices")
    else:
        c.execute("SELECT device_id, device_name, (strftime('%s','now') - strftime('%s', last_seen)) as sec_diff FROM devices WHERE username=?", (session['username'],))
        
    rows = c.fetchall()
    conn.close()
    
    devices = []
    for row in rows:
        status = "online" if row[2] is not None and row[2] < 20 else "offline"
        devices.append({
            "id": row[0],
            "name": row[1],
            "status": status
        })
    return jsonify(devices), 200

# API nhận dữ liệu cảm biến từ ESP32
@app.route('/api/sensor', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.get_json()
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        light = data.get('light')
        
        if temperature is not None and humidity is not None:
            ai_status = analyze_anomaly(temperature, humidity, light)
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO sensor_data (temperature, humidity, light, ai_status) VALUES (?, ?, ?, ?)", 
                      (temperature, humidity, light, ai_status))
            
            if "BAT THUONG" in ai_status:
                action = f"CANH BAO: {ai_status.replace('BAT THUONG: ', '')}"
                c.execute("INSERT INTO device_logs (action) VALUES (?)", (action,))
                # Tạo thông báo cho admin
                c.execute("INSERT INTO notifications (title, message, type, username) VALUES (?, ?, ?, ?)",
                          ("Canh bao cam bien", ai_status[:100], "danger", "admin"))
                
            conn.commit()
            conn.close()
            
            # Kiểm tra quy tắc tự động
            check_auto_rules(temperature, humidity, light)
            
            return jsonify({"status": "success", "ai_status": ai_status}), 201
            
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API lấy dữ liệu cảm biến
@app.route('/api/sensor', methods=['GET'])
def get_sensor_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT temperature, humidity, light, ai_status, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    
    data = [{"temperature": row[0], "humidity": row[1], "light": row[2], "ai_status": row[3] or "Khong ro", "timestamp": row[4]} for row in rows]
    return jsonify(data), 200

# API LED
@app.route('/api/led', methods=['POST'])
def update_led_state():
    try:
        data = request.get_json()
        device_id = data.get('device_id') # e.g. "led_4" or "sensor_auto"
        state = data.get('state')
        
        if device_id and state in [0, 1]:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("UPDATE device_state SET led_state = ? WHERE device_id = ?", (state, device_id))
            
            action = f"Cap nhat {device_id} -> {state} (Web)"
            c.execute("INSERT INTO device_logs (action) VALUES (?)", (action,))
            
            if 'username' in session:
                user_action = f"Thay doi {device_id} sang {'Bat' if state == 1 else 'Tat'}"
                c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (session['username'], user_action))
            
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": f"{device_id} state updated to {state}"}), 200
        return jsonify({"status": "error", "message": "Invalid params"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/led', methods=['GET'])
def get_led_state():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT device_id, led_state FROM device_state")
    rows = c.fetchall()
    conn.close()
    
    res = {}
    for device_id, state in rows:
        res[device_id] = state
        if device_id.startswith("led_"):
            pin_num = device_id.split("_")[1]
            res[pin_num] = state
    return jsonify(res), 200

# API Logs
@app.route('/api/logs', methods=['GET'])
def get_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT action, timestamp FROM device_logs ORDER BY timestamp DESC LIMIT 15")
    rows = c.fetchall()
    conn.close()
    
    data = [{"action": row[0], "timestamp": row[1]} for row in rows]
    return jsonify(data), 200

# API User Logs
@app.route('/api/user_logs', methods=['GET'])
def get_user_logs():
    if 'logged_in' not in session:
        return jsonify([]), 401
        
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if session.get('role') in ['admin', 'technician']:
        c.execute("SELECT username, action, timestamp FROM user_logs ORDER BY timestamp DESC LIMIT 50")
    else:
        c.execute("SELECT username, action, timestamp FROM user_logs WHERE username=? ORDER BY timestamp DESC LIMIT 50", (session['username'],))
        
    rows = c.fetchall()
    conn.close()
    
    logs = [{"username": r[0], "action": r[1], "timestamp": r[2]} for r in rows]
    return jsonify(logs), 200

# API Thống kê nâng cao
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Thống kê cảm biến
    c.execute("SELECT MAX(temperature), MIN(temperature), AVG(temperature) FROM sensor_data")
    t_stats = c.fetchone()
    c.execute("SELECT MAX(humidity), MIN(humidity), AVG(humidity) FROM sensor_data")
    h_stats = c.fetchone()
    c.execute("SELECT MAX(light), MIN(light), AVG(light) FROM sensor_data WHERE light IS NOT NULL")
    l_stats = c.fetchone()
    
    # Tổng thiết bị
    c.execute("SELECT COUNT(*) FROM devices")
    total_devices = c.fetchone()[0]
    
    # Thiết bị online (last_seen < 20 giây)
    c.execute("SELECT COUNT(*) FROM devices WHERE (strftime('%s','now') - strftime('%s', last_seen)) < 20")
    online_devices = c.fetchone()[0]
    
    # Tổng cảnh báo hôm nay
    c.execute("SELECT COUNT(*) FROM device_logs WHERE action LIKE '%CANH BAO%' AND date(timestamp) = date('now')")
    alerts_today = c.fetchone()[0]
    
    # Tổng người dùng
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    # Tổng quy tắc tự động đang bật
    c.execute("SELECT COUNT(*) FROM auto_rules WHERE is_active = 1")
    active_rules = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "temperature": {
            "max": round(t_stats[0], 1) if t_stats[0] else 0,
            "min": round(t_stats[1], 1) if t_stats[1] else 0,
            "avg": round(t_stats[2], 1) if t_stats[2] else 0
        },
        "humidity": {
            "max": round(h_stats[0], 1) if h_stats[0] else 0,
            "min": round(h_stats[1], 1) if h_stats[1] else 0,
            "avg": round(h_stats[2], 1) if h_stats[2] else 0
        },
        "light": {
            "max": round(l_stats[0], 1) if l_stats and l_stats[0] else 0,
            "min": round(l_stats[1], 1) if l_stats and l_stats[1] else 0,
            "avg": round(l_stats[2], 1) if l_stats and l_stats[2] else 0
        },
        "overview": {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "alerts_today": alerts_today,
            "total_users": total_users,
            "active_rules": active_rules
        }
    }), 200

# API Quy tắc tự động hóa
@app.route('/api/auto_rules', methods=['GET', 'POST', 'DELETE'])
def manage_auto_rules():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if request.method == 'POST':
        if session.get('role') not in ['admin', 'technician']:
            conn.close()
            return jsonify({"error": "Khong co quyen"}), 403
            
        data = request.get_json()
        rule_name = data.get('rule_name')
        sensor_type = data.get('sensor_type')
        condition = data.get('condition')
        threshold = data.get('threshold')
        action_type = data.get('action_type', 'led')
        action_value = data.get('action_value', 1)
        pin_target = data.get('pin_target', 4) # Default to GPIO 4
        
        if not all([rule_name, sensor_type, condition, threshold is not None]):
            conn.close()
            return jsonify({"error": "Thieu thong tin"}), 400
        
        c.execute("INSERT INTO auto_rules (rule_name, sensor_type, condition, threshold, action_type, action_value, created_by, pin_target) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (rule_name, sensor_type, condition, threshold, action_type, action_value, session['username'], pin_target))
        c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)",
                  (session['username'], f"Tao quy tac tu dong: {rule_name} cho LED {pin_target}"))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    
    if request.method == 'DELETE':
        if session.get('role') not in ['admin', 'technician']:
            conn.close()
            return jsonify({"error": "Khong co quyen"}), 403
            
        rule_id = request.args.get('id')
        if rule_id:
            c.execute("DELETE FROM auto_rules WHERE id = ?", (rule_id,))
            conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    
    # GET
    c.execute("SELECT id, rule_name, sensor_type, condition, threshold, action_type, action_value, is_active, created_by, timestamp, pin_target FROM auto_rules ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    rules = []
    for r in rows:
        sensor_labels = {"temperature": "Nhiet do", "humidity": "Do am", "light": "Anh sang"}
        rules.append({
            "id": r[0], "name": r[1], "sensor": r[2], "sensor_label": sensor_labels.get(r[2], r[2]),
            "condition": r[3], "threshold": r[4], "action_type": r[5], "action_value": r[6],
            "is_active": r[7], "created_by": r[8], "timestamp": r[9], "pin_target": r[10] or 4
        })
    return jsonify(rules), 200

# API Toggle Auto Rule
@app.route('/api/auto_rules/toggle', methods=['POST'])
def toggle_auto_rule():
    if 'logged_in' not in session or session.get('role') not in ['admin', 'technician']:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    rule_id = data.get('id')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE auto_rules SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

# API Notifications
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    if 'logged_in' not in session:
        return jsonify([]), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if session.get('role') in ['admin', 'technician']:
        c.execute("SELECT id, title, message, type, is_read, timestamp FROM notifications ORDER BY timestamp DESC LIMIT 20")
    else:
        c.execute("SELECT id, title, message, type, is_read, timestamp FROM notifications WHERE username=? ORDER BY timestamp DESC LIMIT 20", (session['username'],))
    
    rows = c.fetchall()
    
    # Đếm chưa đọc
    if session.get('role') in ['admin', 'technician']:
        c.execute("SELECT COUNT(*) FROM notifications WHERE is_read = 0")
    else:
        c.execute("SELECT COUNT(*) FROM notifications WHERE is_read = 0 AND username=?", (session['username'],))
    unread = c.fetchone()[0]
    
    conn.close()
    
    notifs = [{"id": r[0], "title": r[1], "message": r[2], "type": r[3], "is_read": r[4], "timestamp": r[5]} for r in rows]
    return jsonify({"notifications": notifs, "unread": unread}), 200

# API Đánh dấu đã đọc thông báo
@app.route('/api/notifications/read', methods=['POST'])
def mark_notifications_read():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if session.get('role') in ['admin', 'technician']:
        c.execute("UPDATE notifications SET is_read = 1 WHERE is_read = 0")
    else:
        c.execute("UPDATE notifications SET is_read = 1 WHERE is_read = 0 AND username=?", (session['username'],))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

# API xuất báo cáo CSV
@app.route('/api/export', methods=['GET'])
def export_csv():
    import io
    import csv
    from flask import Response
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, temperature, humidity, light, ai_status, timestamp FROM sensor_data ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nhiet Do (C)', 'Do Am (%)', 'Anh Sang (%)', 'Danh Gia AI', 'Thoi Gian'])
    
    for row in rows:
        writer.writerow(row)
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=bao_cao_aiot.csv"}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
