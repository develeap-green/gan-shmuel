from flask import jsonify, request
from sqlalchemy import desc
from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import Transactions, ContainersRegistered
from app.utils import load_weights
from datetime import datetime
import random


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
        logging.error(f"Error: bad values passed into {request.args}: {err}")
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


@app.route('/weight', methods=['POST'])
def post_transaction():
    # if fails should return 415 unsupported
    data = request.get_json()

    if not data:
        logging.error(
            f"no data in request body")
        return {"error": "please provide required parameters in the request body"}, HTTPStatus.BAD_REQUEST

    if data['truck'] and not data['truck'].startswith('T-'):
        logging.error(
            f"Attempted registering truck with invalid license prefixed: {data['truck']}")
        return {"error": "truck license must be prefixed"}, HTTPStatus.BAD_REQUEST

    last_row = db.session.query(Transactions).order_by(
        desc(Transactions.id)).first()

    force = data.get('force') or False
    # truck gets in
    if data['direction'] == 'in':
        if last_row and last_row.direction == 'in' and not force:
            return {"error": "Cannot weight in another truck before another finished"}, HTTPStatus.BAD_REQUEST

        # take data create transaction of in
        session_id = random.randrange(1001, 9999999)
        in_trans = Transactions(datetime=datetime.now(),
                                direction="in",
                                truck=data["truck"],
                                containers=data["containers"],
                                bruto=data["weight"],
                                produce=data['produce'],
                                session_id=session_id)
        db.session.add(in_trans)
        db.session.commit()

        # return data
        return {"id": in_trans.id, "truck": in_trans.truck, "bruto": in_trans.bruto}, HTTPStatus.CREATED

    # weight container
    elif data['direction'] == 'none':
        if last_row and last_row.direction == 'in':
            return {"error": "Cannot weight container until truck weights out"}, HTTPStatus.BAD_REQUEST
        # find weight of a registered container or cancel if not registered
        container = db.session.query(ContainersRegistered).where(
            ContainersRegistered.container_id == data['containers']).one_or_none()

        # unregistered containers are weighted on their own
        if not container:
            if not data.get('unit'):
                error = f"Container {data['containers']} is not registered, cannot register without 'unit' parameter"
                logging.error(error)
                return {"error": error}, HTTPStatus.BAD_REQUEST

            new_container = ContainersRegistered(
                container_id=data['containers'], weight=data['weight'], unit=data['unit'])
            db.seesion.add(new_container)
            db.session.commit()

            return new_container, HTTPStatus.CREATED

        # remove weight of cantainer from data[weight] and add to neto
        session_id = random.randrange(1001, 9999999)
        none_trans = Transactions(datetime=datetime.now(),
                                  direction="none",
                                  containers=container.container_id,
                                  bruto=data["weight"],
                                  neto=data['weight'] - container.weight,
                                  produce=data['produce'],
                                  session_id=session_id)
        db.session.add(none_trans)
        db.session.commit()

        return {"id": none_trans.id, "container": container.container_id, "bruto": none_trans.bruto}, HTTPStatus.CREATED

    # truck gets out
    elif data['direction'] == 'out':
        if last_row and last_row.direction == 'out' and not force:
            return {"error": "weight out is already in session "}, HTTPStatus.BAD_REQUEST

        elif last_row and last_row.direction != 'in' and not (last_row.direction == 'out' and force):
            return {"error": "weight out must be proceeded by a weight in"}, HTTPStatus.BAD_REQUEST

        if not last_row:  # satisfy type checker
            return "imposible path, first row would never be out", HTTPStatus.BAD_REQUEST

        # get all containers weights sum
        if last_row.containers:
            containers = last_row.containers.split(',')
        else:
            containers = ''

        containers = db.session.query(ContainersRegistered).filter(
            ContainersRegistered.container_id.in_(containers)).all()

        session_id = last_row.session_id

        truck_tara = int(data['weight'])

        weights = [c.weight for c in containers]

        if all(isinstance(w, int) for w in weights):
            tara_containers = sum(weights)
            logging.info(
                f"XXXXXXXXXX {truck_tara} {tara_containers} XXXXXXXXXX")
            neto = truck_tara - int(tara_containers)
        else:
            tara_containers = None
            neto = None

        out_trans = Transactions(datetime=datetime.now(),
                                 direction="out",
                                 truck=data['truck'],
                                 bruto=last_row.bruto,
                                 containers=last_row.containers,
                                 truckTara=truck_tara,
                                 neto=neto,
                                 produce=last_row.produce,
                                 session_id=session_id)

        db.session.add(out_trans)
        db.session.commit()

        return {"id": out_trans.id,
                "truck": out_trans.truck,
                "bruto": out_trans.bruto,
                "truckTara": out_trans.truckTara,
                "neto": out_trans.neto,
                }, HTTPStatus.CREATED

    error = f"bad direction argument: expected: \"in,out,none\" - got {data['direction']}"
    logging.error(error)
    return {"error": error}, HTTPStatus.BAD_REQUEST


@app.route('/item/<id>')
def get_item(id):
    # parse query params
    res = {}
    try:
        now = datetime.now()
        to = request.args.get('to', now.strftime('%Y%m%d%H%M%S'))
        _from = request.args.get('from', now.replace(
            day=1, hour=0, minute=0, second=0).strftime('%Y%m%d%H%M%S'))

        _from = datetime.strptime(_from, "%Y%m%d%H%M%S")
        to = datetime.strptime(to, "%Y%m%d%H%M%S")
    except ValueError as err:
        logging.error(f"Error: bad values passed into {request.args}: {err}")
        return "", HTTPStatus.UNPROCESSABLE_ENTITY

    try:
        # handle trucks
        if id[0] == "T":
            transactions = db.session.query(Transactions).filter(
                Transactions.truck == id, Transactions.datetime >= _from, Transactions.datetime <= to).all()
            if transactions:
                session_list = [str(t.session_id) for t in transactions]
                truck_tara = next(
                    (t.truckTara for t in transactions if t.truckTara), None)
                res = {
                    "id": id,
                    "tara": truck_tara,
                    "sessions": session_list
                }
        # handle containers
        elif id[0] == "C":
            transactions = db.session.query(Transactions).filter(
                Transactions.containers.contains(id), Transactions.datetime >= _from, Transactions.datetime <= to).all()

            if transactions:
                container_tara = db.one_or_404(db.session.query(ContainersRegistered).filter(
                    ContainersRegistered.container_id == id))

                session_list = [str(t.session_id) for t in transactions]
                res = {
                    "id": id,
                    "tara": container_tara.weight,
                    "session_id": session_list
                }

        else:
            raise Exception

    except Exception as err:
        logging.error("Item id {id} is either invalid or not in the database")
        return {"error": "invalid item id"}, HTTPStatus.BAD_REQUEST
    if not res:
        return "", HTTPStatus.OK

    return jsonify(res), HTTPStatus.OK


@app.route('/session/<int:id>', methods=['GET'])
def get_session(id):
    transaction = db.one_or_404(db.session.query(
        Transactions).filter_by(session_id=id))

    res = {
        "id": transaction.session_id,
        "truck": transaction.truck,
        "bruto": transaction.bruto,
        "truckTara": transaction.truckTara,
        "neto": transaction.neto,
    }
    return res


@app.route('/batch-weight', methods=['POST'])
def upload_batch_weight():

    file_content = request.data

    if not file_content:
        return {'error': 'No file data found in request body'}, HTTPStatus.BAD_REQUEST

    try:
        return load_weights(file_content)

    except Exception as e:
        return {'error': str(e)}


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
