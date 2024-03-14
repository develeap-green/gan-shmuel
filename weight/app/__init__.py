from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_HOST = os.environ.get('MYSQL_HOST')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/weight'

db = SQLAlchemy()


from app.models import ContainersRegistered, Transactions

db.init_app(app)

