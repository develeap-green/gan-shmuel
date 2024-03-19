import os
from flask import jsonify, request
from sqlalchemy import desc
from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import Transactions, ContainersRegistered
from app.utils import load_weights, detect_file_format, create_directory_if_not_exists, create_file_if_not_exists
from datetime import datetime
import random

UPLOAD_DIRECTORY = '/in'
CSV_FILENAME = 'uploaded_file.csv'
JSON_FILENAME = 'uploaded_file.json'


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

    if data.get('truck') and not data['truck'].startswith('T-'):
        logging.error(
            f"Attempted registering truck with invalid license prefixed: {data['truck']}")
        return {"error": "truck license must be prefixed"}, HTTPStatus.BAD_REQUEST

    last_row = db.session.query(Transactions).order_by(
        desc(Transactions.id)).first()

    force = data.get('force') or False
    # truck gets in
    if data['direction'] == 'in':
        if last_row and last_row.direction == 'in' and not force:
            logging.error(
                "Cannot weight in another truck before another finished")
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

            container_id = data['containers']
            weight = int(data['weight'])
            unit = data['unit']

            new_container = ContainersRegistered(
                container_id=container_id,
                weight=weight,
                unit=unit)

            db.session.add(new_container)
            db.session.commit()

            return {"message": "new container has been added"}, HTTPStatus.CREATED

        # remove weight of cantainer from data[weight] and add to neto
        session_id = random.randrange(1001, 9999999)
        none_trans = Transactions(datetime=datetime.now(),
                                  direction="none",
                                  containers=container.container_id,
                                  bruto=data["weight"],
                                  neto=data['weight'] - container.weight,
                                  produce=data.get("produce") or None,
                                  session_id=session_id)
        db.session.add(none_trans)
        db.session.commit()

        return {"id": none_trans.id, "container": container.container_id, "bruto": none_trans.bruto}, HTTPStatus.CREATED

    # truck gets out
    elif data['direction'] == 'out':
        if last_row and last_row.direction == 'out' and not force:
            logging.error("weight out is already in session")
            return {"error": "weight out is already in session"}, HTTPStatus.BAD_REQUEST

        elif last_row and last_row.direction != 'in' and not (last_row.direction == 'out' and force):
            logging.error("weight out must be proceeded by a weight in")
            return {"error": "weight out must be proceeded by a weight in"}, HTTPStatus.BAD_REQUEST

        if not last_row:  # satisfy type checker
            return "imposible path, first row would never be out", HTTPStatus.BAD_REQUEST

        # get all containers weights sum
        if last_row.containers:
            containers = last_row.containers.split(',')
        else:
            containers = ''

        db_containers = db.session.query(ContainersRegistered).filter(
            ContainersRegistered.container_id.in_(containers)).all()

        # even if force should be correct to hold the prev session
        session_id = last_row.session_id
        truck_tara = int(data['weight'])
        weights = [c.weight for c in db_containers]

        if len(weights) > 0 and all(isinstance(w, int) for w in weights) and len(containers) == len(db_containers):
            tara_containers = sum(weights)
            neto = last_row.bruto - truck_tara - int(tara_containers)
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
            error = f"provided id: {id}, doesn't belong to neither trucks nor containers"
            logging.error(error)
            return {"error": error}, HTTPStatus.BAD_REQUEST

    except Exception as err:
        logging.error("Item id {id} is either invalid or not in the database")
        return {"error": "invalid item id"}, HTTPStatus.BAD_REQUEST

    if not res:
        return "", HTTPStatus.OK

    return jsonify(res), HTTPStatus.OK


@app.route('/session/<int:id>')
def get_session(id):
    transaction = db.one_or_404(db.session.query(
        Transactions).filter_by(session_id=id), description="session doesn't exist")
    res = {
        "id": transaction.session_id,
        "truck": transaction.truck if transaction.truck else 'na',
        "bruto": transaction.bruto,
        "neto": transaction.neto if transaction.neto else 'na',
    }

    if transaction.direction == 'out':
        res = {**res, "truckTara": transaction.truckTara}

    return res, HTTPStatus.OK


@app.route('/batch-weight', methods=['POST'])
def upload_batch_weight():
    file_content = request.data

    if not file_content:
        logging.error('No file data found in request body')
        return {'error': 'No file data found in request body'}, HTTPStatus.BAD_REQUEST

    # Determine file format
    file_format = detect_file_format(file_content)

    if file_format == 'csv':
        filepath = os.path.join(UPLOAD_DIRECTORY, CSV_FILENAME)
        create_directory_if_not_exists(UPLOAD_DIRECTORY)
        create_file_if_not_exists(filepath)
    elif file_format == 'json':
        filepath = os.path.join(UPLOAD_DIRECTORY, JSON_FILENAME)
        create_directory_if_not_exists(UPLOAD_DIRECTORY)
        create_file_if_not_exists(filepath)
    else:
        error_message = "Unsupported file format. Please provide a CSV or JSON file."
        logging.error(error_message)
        return {'error': error_message}, HTTPStatus.BAD_REQUEST
    try:
        with open(filepath, 'wb') as f:
            f.write(file_content)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    try:
        return load_weights(filepath, file_format)
    except Exception as e:
        logging.error(str(e))
        return {'error': str(e)}, HTTPStatus.BAD_REQUEST


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
        return {'status': 'success', 'message': 'Ok'}, HTTPStatus.OK

    except Exception as err:
        logging.error(f"Database connection error: {err}")
        return {'status': 'error', 'message': 'Error'}, HTTPStatus.SERVICE_UNAVAILABLE
