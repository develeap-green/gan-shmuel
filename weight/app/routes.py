from operator import contains
from venv import logger
from flask import jsonify, request
from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import ContainersRegistered, Transactions
from datetime import datetime
import csv


@app.route('/session/<int:id>', methods=['GET'])
def get_session(id):
    transaction = db.one_or_404(db.session.query(
        Transactions).filter_by(session_id=id))
    try:
        res = {
            "id": transaction.session_id,
            "truck": transaction.truck,
            "bruto": transaction.bruto,
            "truckTara": transaction.truckTara,
            "neto": transaction.neto,
        }
        return res
    except:
        return "404 no session id"


@app.route('/weight')
def retrieve_weight_list():
    try:
        now = datetime.now()

        _filter = request.args.get('filter', 'in,out,none')
        _from = request.args.get('from', now.replace(
            hour=0, minute=0, second=0).strftime("%Y%m%d%H%M%S"))
        to = request.args.get('to', now.strftime("%Y%m%d%H%M%S"))

        _from = datetime.strptime(_from, "%Y%m%d%H%M%S")
        to = datetime.strptime(to, "%Y%m%d%H%M%S")

    except ValueError as err:
        logger.error(f"Error: bad values passed into {request.args}: {err}")
        return "", HTTPStatus.UNPROCESSABLE_ENTITY

    transactions = db.session.query(Transactions).filter(Transactions.datetime >= _from,
                                                         Transactions.datetime <= to,
                                                         Transactions.direction.in_(_filter.split(','))).all()

    res = [{
        "id": t.id,
        "direction": t.direction,
        "bruto": t.bruto,
        "neto": t.neto if t.neto else None,
        "produce": t.produce,
        "containers": [container for container in t.containers.split(',')] or [],
    } for t in transactions]

    return jsonify(res), HTTPStatus.OK


@app.route('/unknown')
def get_uknown_containers():
    containers = db.session.query(ContainersRegistered).filter(
        ContainersRegistered.weight == None).all()
    res = [c.container_id for c in containers]

    if not res:
        return '', HTTPStatus.NOT_FOUND

    return jsonify(res), HTTPStatus.OK


@app.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        return '', HTTPStatus.OK

    except Exception as err:
        logging.error(f"Database connection error: {err}")
        return '', HTTPStatus.SERVICE_UNAVAILABLE

# GET /item/<id>?from=t1&to=t2
# - id is for an item (truck or container). 404 will be returned if non-existent
# - t1,t2 - date-time stamps, formatted as yyyymmddhhmmss. server time is assumed.
# default t1 is "1st of month at 000000". default t2 is "now".
# Returns a json:
# { "id": <str>,
#   "tara": <int> OR "na", // for a truck this is the "last known tara"
#   "sessions": [ <id1>,...]
# }


def find_weight_by_id(csv_file, search_id):
    try:
        with open(csv_file, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['id'] == search_id:
                    return row['kg']
    except:
        return "na"


@app.route('/item/<id>')
def get_item(id):
    now = datetime.now()
    _from = ''
    to = ""
    monnth = ""
    session_list = []
    try:
        if not request.args.get('to'):
            to = datetime.now()
        else:
            to = request.args.get('to')
        if not request.args.get('from'):
            hms = "000000"
            monnth = str(datetime.today().month)
            if len(monnth) == 1:
                monnth = "0" + monnth
            _from = str(datetime.today().year) + \
                monnth + "01" + hms
        else:
            _from = request.args.get('from')
        to = request.args.get('to', now.strftime("%Y%m%d%H%M%S"))
        _from = datetime.strptime(_from, "%Y%m%d%H%M%S")
        to = datetime.strptime(to, "%Y%m%d%H%M%S")
        if id[0] == "T":
            transaction = db.session.query(Transactions).filter(
                Transactions.truck == id, Transactions.datetime >= _from, Transactions.datetime <= to).all()
            for t in transaction:
                session_list.append(str(t.session_id))
            if transaction:
                res = [{
                    "id": id,
                    "tara": t.truckTara,
                    "sessions": session_list
                } for t in transaction]
                return jsonify(res), HTTPStatus.OK
        elif id[0] == "C":
            transaction = db.session.query(Transactions).filter(
                Transactions.containers.contains(id), Transactions.datetime >= _from, Transactions.datetime <= to).all()
            container_tara = find_weight_by_id(
                "data/containers1.csv", id) or "na"
            for t in transaction:
                session_list.append(str(t.session_id))
            if transaction:
                res = [{
                    "id": id,
                    "tara": container_tara,
                    "session_id": session_list
                }]
                return jsonify(res), HTTPStatus.OK
    except:
        logger.error(f"Error: bad values passed into {request.args}")
        return "", HTTPStatus.UNPROCESSABLE_ENTITY
    return "item not found"
