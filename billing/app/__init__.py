from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# For local testing, use '127.0.0.1' to connect to the container
# MYSQL_HOST = '127.0.0.1'

# Retrieve MySQL environment variables from Docker Compose
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'db')  # Default to localhost if not provided
MYSQL_USER = os.environ.get('MYSQL_USER', 'user')       # Default to 'user' if not provided
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'pass')  # Default to 'pass' if not provided

# Configure SQLAlchemy database URI using the environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/billing'

# Suppress SQLAlchemy deprecation warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)