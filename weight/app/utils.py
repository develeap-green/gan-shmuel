import csv
import json
import os
from app import db
import logging
from http import HTTPStatus
from app.models import ContainersRegistered


def load_weights(file_path, file_format):
    with open(file_path, 'r') as file:
        file_content = file.read()

    if file_format == 'csv':
        return register_container_csv(file_content)
    elif file_format == 'json':
        return register_container_json(file_content)


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_file_if_not_exists(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'w').close()


def detect_file_format(file_content):
    try:
        file_content = file_content.decode('utf-8')
        if is_json(file_content):
            return 'json'
        elif is_csv(file_content):
            return 'csv'
        else:
            return None
    except Exception as e:
        return None


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
    if not container_id.startswith("C-"):
        container_id = "C-" + container_id
    return container_id


def validate_weight(weight):
    if weight == "":
        return None
    try:
        return float(weight)
    except (ValueError, TypeError):
        logging.error("Invalid weight format. Expected a numeric value.")
        return None


def validate_unit(unit):
    return unit in ['kg', 'lbs']


def register_container_csv(file_content):
    reader = csv.reader(file_content.splitlines())
    header = next(reader)
    expected_headers = [['id', 'kg'], ['id', 'lbs']]

    if header not in expected_headers:
        error_message = "Invalid CSV header. Expected ('id', 'kg') or ('id', 'lbs')."
        logging.error(error_message)
        return {'error': error_message}, HTTPStatus.BAD_REQUEST

    existing_container_ids = {row[0] for row in db.session.query(
        ContainersRegistered.container_id).all()}
    containers_to_add = set()

    for row in reader:
        if len(row) not in [1, 2]:
            logging.error("Invalid number of columns in CSV row.")
            continue

        container_id = validate_container_id(row[0])
        if container_id is None or container_id in existing_container_ids:
            continue

        weight = validate_weight(row[1]) if len(row) == 2 else None
        unit = header[1] if len(row) == 2 else None

        containers_to_add.add((container_id, weight, unit))
    db.session.bulk_insert_mappings(ContainersRegistered, [
                                    {"container_id": c_id, "weight": weight, "unit": unit} for c_id, weight, unit in containers_to_add])
    db.session.commit()
    return {'message': 'success'}, HTTPStatus.CREATED


def register_container_json(file_content):
    data = json.loads(file_content)

    existing_container_ids = {row[0] for row in db.session.query(
        ContainersRegistered.container_id).all()}
    containers_to_add = set()

    for item in data:
        if not isinstance(item, dict) or 'id' not in item:
            error_message = "Invalid JSON format. Each item should have 'id' key."
            logging.error(error_message)
            return {'error': error_message}, HTTPStatus.BAD_REQUEST

        container_id = validate_container_id(item['id'])
        if container_id is None or container_id in existing_container_ids:
            continue

        weight = validate_weight(item.get('weight'))
        unit = item.get('unit')

        containers_to_add.add((container_id, weight, unit))

    db.session.bulk_insert_mappings(ContainersRegistered, [
                                    {"container_id": c_id, "weight": weight, "unit": unit} for c_id, weight, unit in containers_to_add])
    db.session.commit()
    return {'message': 'success'}, HTTPStatus.CREATED
