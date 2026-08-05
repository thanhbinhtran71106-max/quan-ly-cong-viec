from flask import Blueprint

iot_bp = Blueprint('iot', __name__)

from . import routes
