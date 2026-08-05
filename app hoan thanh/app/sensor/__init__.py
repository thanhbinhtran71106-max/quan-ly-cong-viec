from flask import Blueprint

sensor_bp = Blueprint('sensor', __name__)

from . import routes
