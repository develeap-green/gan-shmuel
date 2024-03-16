from flask import jsonify, request
from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import Transactions
from datetime import datetime
import random


@app.route('/weight', methods=['POST'])
def handle_post():
     # TODO ERROR HANDLING
    # try:
        data = request.get_json()
        curr_direction = data['direction']
        new_session_id = random.random() * random.random()
        # TODO take later form csv
        sum_tara_containaris = 500
        # get last truck session
        results = Transactions.query.filter_by(truck = data['truck']).order_by(Transactions.datetime.desc())
        if results.count() > 1:
            last_session_id = results[0].session_id
            last_direction = results[0].direction   
        response = {
            "truck": data["truck"],
        }
        # if in == in out == out
        if last_direction == curr_direction:
            if data["force"] == "false":
                return f"force is false, last_direction {last_direction} , curr_direction {curr_direction}"
            # force update a record
            else:
                if data["direction"] in ["in", "none"]:
                    new_session_id = random.random()
                    bruto = data["weight"]
                    response["bruto"] = bruto

                # direction is out
                else:
                    truck_tara = data["weight"]
                    neto = bruto - truck_tara - sum_tara_containaris
                    new_session_id = last_session_id
                    response["truck_tara"] = truck_tara
                    response["neto"] = neto
        #  last session direction != req direction
        trasn_obj = Transactions(
                    direction = data['direction'],
                    truck = data['truck'],
                    containers = data['containers'],
                    produce = data['produce'],
                    datetime = datetime.now(),
                    session_id = new_session_id,
                    )
                
        db.session.add(trasn_obj)
        db.session.commit()
        return response
    # except:
    #     return "error"

@app.route('/session/<int:id>', methods=['GET'])
def get_session(id):
        transaction = db.one_or_404(Transactions.query.filter_by(session_id=id))
        try:
            res = {
                "id" : transaction.session_id,
                "truck": transaction.truck,
                "bruto": transaction.bruto,
                "truckTara": transaction.truckTara,
                "neto": transaction.neto,
            }
            return res
        except:
            return "404 no session id"
            

    
    
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
