import http.server
import socketserver
import json
import urllib.parse
import time

devices_config = [
    {"id": i, "name": f"LED {i+1}", "pin": p, "state": 0}
    for i, p in enumerate([4, 5, 6, 7, 15, 16, 17, 18])
]
activity_logs = []

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()
    start_str = 'def get_html():\n    return """'
    start_idx = content.find(start_str)
    if start_idx != -1:
        start_idx += len(start_str)
        end_idx = content.find('"""', start_idx)
        HTML = content[start_idx:end_idx]
    else:
        HTML = "<h1>Lỗi đọc file</h1>"

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global devices_config, activity_logs
        
        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)
        
        if url.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
            
        elif url.path == '/api/devices':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(devices_config).encode('utf-8'))
            
        elif url.path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(activity_logs).encode('utf-8'))
            
        elif url.path == '/api/led':
            try:
                id_val = int(qs.get('id', [None])[0])
                state_val = int(qs.get('state', [None])[0])
                log_val = qs.get('log', [None])[0]
                
                for d in devices_config:
                    if d['id'] == id_val:
                        d['state'] = state_val
                        break
                if log_val:
                    activity_logs.insert(0, log_val)
                    if len(activity_logs) > 10: activity_logs.pop()
            except:
                pass
                
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"OK")
            
        elif url.path == '/api/device/add':
            name = qs.get('name', ["New Device"])[0]
            pin = int(qs.get('pin', [-1])[0])
            new_id = int(time.time())
            devices_config.append({"id": new_id, "name": name, "pin": pin, "state": 0})
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"OK")
            
        elif url.path == '/api/device/remove':
            remove_id = int(qs.get('id', [-1])[0])
            devices_config = [d for d in devices_config if d['id'] != remove_id]
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", 8080), Handler) as httpd:
    print("Serving at port 8080. Open http://localhost:8080")
    httpd.serve_forever()
