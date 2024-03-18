import csv
import json
from flask import jsonify, request
from app import app, db
from sqlalchemy.sql import text
import logging
from http import HTTPStatus
from datetime import datetime
from app.models import Transactions, ContainersRegistered
from app.models import ContainersRegistered, Transactions
from datetime import datetime


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


@app.route('/batch-weight', methods=['POST'])
def upload_batch_weight():

    file_content = request.data

    if not file_content:
        return jsonify({'error': 'No file data found in request body'})

    try:
        load_weights(file_content)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})


def load_weights(file_content):

    # Convert file content to a string
    file_content = file_content.decode('utf-8')

    # Determine if the content represents JSON data or CSV
    if is_json(file_content):
        register_container_json(file_content)
    elif is_csv(file_content):
        register_container_csv(file_content)
    else:
        logging.error(
            "Unsupported file format. Please provide a CSV or JSON file.")
        raise ValueError(
            "Unsupported file format. Please provide a CSV or JSON file.")


def is_json(file_content):
    try:
        json.loads(file_content)
        return True
    except ValueError:
        return False


def is_csv(file_content):
    try:
        csv.Sniffer().sniff(file_content)
        return True
    except csv.Error:
        return False


def validate_container_id(container_id):
    return container_id.startswith(("C-", "K-")) and container_id[2:].isdigit()


def validate_weight(weight):
    try:
        float(weight)
        return True
    except (ValueError, TypeError):
        logging.error("Invalid weight format. Expected a numeric value.")
        return False


def validate_unit(unit):
    return unit in ['kg', 'lbs']


def register_container_csv(file_content):
    reader = csv.reader(file_content.splitlines())
    header = next(reader)
    expected_headers = [['id', 'kg'], ['id', 'lbs']]

    if header not in expected_headers:
        logging.error(
            "Invalid CSV header. Expected ('id', 'kg') or ('id', 'lbs').")
        raise ValueError(
            "Invalid CSV file. Expected ('id', 'kg') or ('id', 'lbs').")

    existing_container_ids = {row[0] for row in db.session.query(
        ContainersRegistered.container_id).all()}
    containers_to_add = set()

    for row in reader:
        if len(row) != 2:
            logging.error("Invalid number of columns in CSV row.")
            continue

        container_id, weight = row[0], row[1]

        if not (validate_container_id(container_id) and validate_weight(weight)):
            continue

        if container_id in existing_container_ids:
            logging.info(
                f"Container with ID {container_id} already exists in the database. Skipping...")
            continue

        unit = header[1]
        containers_to_add.add((container_id, float(weight), unit))

    db.session.bulk_insert_mappings(ContainersRegistered, [
                                    {"container_id": c_id, "weight": weight, "unit": unit} for c_id, weight, unit in containers_to_add])
    db.session.commit()


def register_container_json(file_content):
    data = json.loads(file_content)

    existing_container_ids = {row[0] for row in db.session.query(
        ContainersRegistered.container_id).all()}
    containers_to_add = set()

    for item in data:
        if not isinstance(item, dict) or 'id' not in item or 'weight' not in item or 'unit' not in item:
            logging.error(
                "Invalid JSON format. Each item should have 'id', 'weight', and 'unit' keys.")
            raise ValueError(
                "Invalid JSON format. Each item should have 'id', 'weight', and 'unit' keys.")

        container_id, weight, unit = item['id'], item['weight'], item['unit']

        if not (validate_container_id(container_id) and validate_weight(weight) and validate_unit(unit)):
            continue

        if container_id in existing_container_ids:
            logging.info(
                f"Container with ID {container_id} already exists in the database. Skipping...")
            continue

        containers_to_add.add((container_id, float(weight), unit))

    db.session.bulk_insert_mappings(ContainersRegistered, [
                                    {"container_id": c_id, "weight": weight, "unit": unit} for c_id, weight, unit in containers_to_add])
    db.session.commit()
# GET /item/<id>?from=t1&to=t2
# - id is for an item (truck or container). 404 will be returned if non-existent
# - t1,t2 - date-time stamps, formatted as yyyymmddhhmmss. server time is assumed.
# default t1 is "1st of month at 000000". default t2 is "now".
# Returns a json:
# { "id": <str>,
#   "tara": <int> OR "na", // for a truck this is the "last known tara"
#   "sessions": [ <id1>,...]
# }


@app.route('/item/<id>')
def get_item(id):
    # parse query params
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
                res = {
                    "id": id,
                    "tara": transactions[0].truckTara,
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
        return "", HTTPStatus.NOT_FOUND

    return jsonify(res), HTTPStatus.OK
