import csv
import json
from app import db
import logging
from http import HTTPStatus
from app.models import ContainersRegistered


def load_weights(file_content):

    # Convert file content to a string
    file_content = file_content.decode('utf-8')

    # Determine if the content represents JSON data or CSV
    if is_json(file_content):
        return register_container_json(file_content)
    elif is_csv(file_content):
        return register_container_csv(file_content)
    else:
        error_message = "Unsupported file format. Please provide a CSV or JSON file."
        logging.error(error_message)
        return {'error': error_message}, HTTPStatus.BAD_REQUEST


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
    return container_id.startswith(("C-")) and container_id[2:].isdigit()


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
        error_message = "Invalid CSV header. Expected ('id', 'kg') or ('id', 'lbs')."
        logging.error(error_message)
        return {'error': error_message}, HTTPStatus.BAD_REQUEST

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
    return {'message': 'success'}, HTTPStatus.CREATED


def register_container_json(file_content):
    data = json.loads(file_content)

    existing_container_ids = {row[0] for row in db.session.query(
        ContainersRegistered.container_id).all()}
    containers_to_add = set()

    for item in data:
        if not isinstance(item, dict) or 'id' not in item or 'weight' not in item or 'unit' not in item:
            error_message = "Invalid JSON format. Each item should have 'id', 'weight', and 'unit' keys."
            logging.error(error_message)
            return {'error': error_message}, HTTPStatus.BAD_REQUEST

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
    return {'message': 'success'}, HTTPStatus.CREATED
