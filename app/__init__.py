from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Inject timedelta into templates
    from datetime import timedelta
    app.jinja_env.globals['timedelta'] = timedelta

    from app.routes.main import main_bp
    from app.routes.employees import employees_bp
    from app.routes.tasks import tasks_bp
    from app.routes.schedules import schedules_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(schedules_bp, url_prefix='/schedules')

    return app


from app import models  # noqa: E402, F401
