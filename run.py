import os
import sys
import webbrowser
import threading
import time

def check_requirements():
    try:
        import flask
        import flask_sqlalchemy
        import flask_migrate
    except ImportError:
        print("Installing required packages...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")

check_requirements()

from app import create_app, db

app = create_app()

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("=" * 60)
    print("EMPLOYEE TASK SCHEDULER IS RUNNING...")
    print("URL: http://127.0.0.1:5000")
    print("=" * 60)

    # Automatically open web browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask Server
    app.run(host='127.0.0.1', port=5000, debug=True)
