import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Database (Default to SQLite for local development without requiring local PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'aiot_v2.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT
    MQTT_BROKER_URL = os.environ.get('MQTT_BROKER_URL') or 'localhost'
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT') or 1883)
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False
