from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus

@app.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        db.session.close()  
        # return jsonify({"status": "OK", "code": HTTPStatus.OK}), HTTPStatus.OK
        return '', HTTPStatus.OK
    
    except Exception as err:
        logging.error(f"Database connection error: {err}")
        error = {"status": "Service Unavailable", "code": HTTPStatus.SERVICE_UNAVAILABLE}
        # return jsonify(error), HTTPStatus.SERVICE_UNAVAILABLE
        return '', HTTPStatus.SERVICE_UNAVAILABLE