from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import flask_excel as excel

app = Flask(__name__)
excel.init_excel(app)

# Configure logging to output to a file - DISABLED FOR NOW
# log_file = './logs/app.log'  # Path to the log file

# Configure the root logger
# logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Retrieve MySQL environment variables from Docker Compose
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql-billing')  # Default to db if not provided
MYSQL_USER = os.environ.get('MYSQL_USER', 'user')       # Default to 'user' if not provided
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'pass')  # Default to 'pass' if not provided

# Construct database URI dynamically
DB_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/billing'

# Configure SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# Suppress SQLAlchemy deprecation warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
