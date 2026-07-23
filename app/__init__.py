from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.employee import bp as employee_bp
    app.register_blueprint(employee_bp, url_prefix='/employee')

    from app.routes.task import bp as task_bp
    app.register_blueprint(task_bp, url_prefix='/task')
    
    from app.routes.schedule import bp as schedule_bp
    app.register_blueprint(schedule_bp, url_prefix='/schedule')

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Automatically create database tables if they don't exist
    with app.app_context():
        from app.models import employee, task, schedule
        db.create_all()

    return app
