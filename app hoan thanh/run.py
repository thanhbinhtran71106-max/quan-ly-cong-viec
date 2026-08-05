import threading
import webbrowser
from app import create_app, socketio

app = create_app()

def open_browser():
    webbrowser.open_new("http://localhost:5000/dashboard")

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, use_reloader=False)
