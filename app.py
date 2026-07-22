from flask import Flask
from models import db
from config import Config
from routes import employees_bp, tasks_bp, schedules_bp, dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo database
    db.init_app(app)

    # Đăng ký Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(schedules_bp)

    # Tạo bảng nếu chưa có
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("  Employee Task Scheduler đang chạy!")
    print("  Truy cập: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
