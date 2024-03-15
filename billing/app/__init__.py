from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_HOST = os.environ.get('MYSQL_HOST')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql-user:sql-password@db/db'

db = SQLAlchemy()