from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
import os
import logging
load_dotenv()

FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
BASE_URL = os.environ.get('BASE_URL')

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# App config
logger.info('Initializing Flask app')
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# CORS config
allowed_origins = [
    "http://localhost:8080",
    BASE_URL
]
cors = CORS(app, resources={
    r"/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    }
})

# Import routes
logger.info('Importing routes')
from app import routes