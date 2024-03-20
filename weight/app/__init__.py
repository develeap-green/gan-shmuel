from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os

MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_HOST = os.environ.get('MYSQL_HOST')

base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/weight'
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'in')

db = SQLAlchemy()
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

from app.models import ContainersRegistered, Transactions

db.init_app(app)

from app import routes
