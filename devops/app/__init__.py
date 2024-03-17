from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from flask_mail import Mail
import os
import logging
load_dotenv()

FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
REPO_URL = os.environ.get('REPO_URL')
REPO_NAME = REPO_URL.split('/')[-1].split('.git')[0]

MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
SENDER_NAME = os.environ.get('SENDER_NAME')

# Logger config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# App config
logger.info('Initializing Flask app')
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Email config
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = (SENDER_NAME, MAIL_DEFAULT_SENDER)
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

# Import routes
logger.info('Importing routes')
from app import routes