import json
import asyncio
import sqlite3
import csv
from io import StringIO
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="Health Monitor Professional Dashboard")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ file tĩnh
app.mount("/static", StaticFiles(directory="static"), name="static")

import os

# 1. Khởi tạo Database SQLite để lưu trữ lịch sử
DB_DIR = r"D:\HealthMonitorData"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_FILE = os.path.join(DB_DIR, "health_data.db")
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            bpm INTEGER,
            spo2 INTEGER,
            body_temp REAL,
            room_temp REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Hàm ghi dữ liệu
def log_vitals(bpm, spo2, body_temp, room_temp, humidity):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO vitals (bpm, spo2, body_temp, room_temp, humidity)
        VALUES (?, ?, ?, ?, ?)
    ''', (bpm, spo2, body_temp, room_temp, humidity))
    conn.commit()
    conn.close()

# Quản lý WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                pass

manager = ConnectionManager()

# Router Trang Chủ
@app.get("/")
async def get():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# 2. Router Xuất file CSV (Export Report)
@app.get("/api/export")
async def export_csv():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, bpm, spo2, body_temp, room_temp, humidity FROM vitals ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    # Trả về file dạng CSV tải xuống
    f = StringIO()
    writer = csv.writer(f)
    writer.writerow(['Thời gian (Timestamp)', 'Nhịp tim (BPM)', 'SpO2 (%)', 'Nhiệt độ Cơ thể (C)', 'Nhiệt độ Phòng (C)', 'Độ ẩm (%)'])
    for row in rows:
        writer.writerow(row)
    
    f.seek(0)
    response = StreamingResponse(iter([f.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=Patient_Vitals_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return response

# Timer để tránh ghi Database liên tục làm nặng máy
last_log_time = 0

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global last_log_time
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Broadcast dữ liệu sóng ECG siêu mượt cho giao diện
            await manager.broadcast(data)
            
            # Ghi vào database định kỳ (mỗi 2 giây) để lưu lịch sử
            now = asyncio.get_event_loop().time()
            if now - last_log_time > 2.0:
                try:
                    parsed = json.loads(data)
                    if 'bpm' in parsed and 'spo2' in parsed:
                        log_vitals(
                            parsed.get('bpm'), 
                            parsed.get('spo2'), 
                            parsed.get('body_temp'), 
                            parsed.get('room_temp'), 
                            parsed.get('humidity')
                        )
                        last_log_time = now
                except:
                    pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
