<<<<<<< HEAD
from flask import jsonify, request
from app import app, db
=======
from app import app
from flask import request
from app import db
from app.models import Transactions, ContainersRegistered
from datetime import datetime
>>>>>>> weight-main
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import Transactions

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
        return '', HTTPStatus.OK
    
    except Exception as err:
        logging.error(f"Database connection error: {err}")
        return '', HTTPStatus.SERVICE_UNAVAILABLE

@app.route('/weight')
def retrieve_weight_list():
    try:
        _from = request.args.get('from')
        to = request.args.get('to')
        _filter =  request.args.get('filter', 'in,out,none')

        logging.info(f"from: {_from}, to: {to}, filter: {_filter}")

        _from = datetime.strptime(_from, "%Y%m%d%H%M%S")
        to = datetime.strptime(to, "%Y%m%d%H%M%S")

    except KeyError as err:
        logging.error(f"Bad query params keys: {err}")
        return '', HTTPStatus.BAD_REQUEST
    except ValueError as err:
        logging.error(f"Bad query params values: {err}")
    
    else:
        query = Transactions.query.filter(Transactions.datetime >= _from,
                                        Transactions.datetime <= to)
        
        transactions = query.filter(Transactions.direction.ilike(_filter)).all()
        
        res = [transaction.to_dict() for transaction in transactions]
        
        if not res:
            return '', HTTPStatus.NOT_FOUND
        
        return jsonify(res), HTTPStatus.OK
