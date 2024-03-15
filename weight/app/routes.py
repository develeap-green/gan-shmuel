from flask import jsonify, request
from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import Transactions

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