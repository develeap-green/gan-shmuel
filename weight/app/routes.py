from app import app
from flask import request
from app import db
from app.models import Transactions, ContainersRegistered
from datetime import datetime
from sqlalchemy.sql import text
import logging
from http import HTTPStatus

auto_increment_number = 0
date_time = datetime.now()
format = '%Y-%m-%d %H:%M:%S'

def generate_new_session_id():
    global auto_increment_number
    auto_increment_number += 1
    return auto_increment_number

@app.route('/')
def example():
    return 200

@app.route('/weight', methods=['POST'])
def handle_post():
    try:
        if request.json['direction'] in ["none", "in"]:
            generate_new_session_id()
        
        transaction_obj = Transactions(
            direction=request.json['direction'],
            truck=request.json['truck'],
            containers=request.json['containers'],
            produce=request.json['produce'],
            session_id = auto_increment_number,
            datetime=date_time.strftime(format)     
        )
        
        container_obj = ContainersRegistered(
            weight=int(request.json['weight']),
            unit=request.json['unit']
        )
        db.session.add(container_obj)

        if request.json['direction']  == 'out':
            transaction_obj.truckTara
            transaction_obj.neto

        db.session.add(transaction_obj)
        db.session.add(container_obj)
        db.session.commit()

        response_data = {
            "id": transaction_obj.id,
            "truck": transaction_obj.truck,
            "bruto": transaction_obj.bruto
        }
    
        return response_data
    except Exception:
        return "error happend"

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
