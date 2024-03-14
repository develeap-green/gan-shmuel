from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql-user:sql-password@db/db'

db = SQLAlchemy()


