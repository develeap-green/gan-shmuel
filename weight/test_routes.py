from datetime import datetime
from http import HTTPStatus
import pytest
import json
from app import app, db, routes
from app.models import ContainersRegistered, Transactions
import requests
from random import sample
import string
import random


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def base_url():
    return "http://127.0.0.1:5000"


def test_retrieve_weight_list_success(base_url):
    url = f"{base_url}/weight?filter=in,out&from=20230101000000&to=20250101000000"
    response = requests.get(url)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Check if data is either an empty list or a list of transactions
    assert isinstance(data, list) or data == []

    # # If data is not empty, iterate over each transaction in the response and check the fields
    # if data:
    #     for transaction in data:
    #         assert datetime.strptime(transaction["datetime"], "%Y-%m-%d %H:%M:%S") >= datetime(2023, 1, 1, 0, 0, 0)
    #         assert datetime.strptime(transaction["datetime"], "%Y-%m-%d %H:%M:%S") <= datetime(2025, 1, 1, 0, 0, 0)

    #         # Ensure 'containers' is a list
    #         assert isinstance(transaction["containers"], list)


def test_retrieve_weight_list_bad_values(base_url):
    url = f"{base_url}/weight?filter=in,out&from=invalid_date&to=20240101000000"
    response = requests.get(url)
    assert response.status_code == 422


def test_retrieve_weight_list_bad_values(base_url):
    url = f"{base_url}/weight"
    response = requests.get(url)
    assert response.status_code == 200


def test_health_check(base_url):
    url = f"{base_url}/health"
    response = requests.get(url)
    assert response.status_code == 200


def test_upload_batch_weight_empty_request(client):
    response = client.post('/batch-weight')
    assert response.status_code == 400
    assert response.json == {'error': 'No file data found in request body'}


def test_upload_batch_weight_invalid_json(client):
    response = client.post('/batch-weight', data={'key': 'value'})
    assert response.status_code == 400


def test_upload_batch_weight_invalid_csv(client):
    response = client.post('/batch-weight', data=b'not a csv file')
    assert response.status_code == 400


def test_upload_batch_weight_unsupported_format(client):
    response = client.post('/batch-weight', data=b'unsupported format')
    assert response.status_code == 400


def test_upload_batch_weight_success(base_url):
    # Data to be sent in the POST request
    data = [
        {"id": "C-001", "weight": 10.5, "unit": "kg"},
        {"id": "C-002", "weight": 15, "unit": "lbs"}
    ]

    # Convert data to JSON string
    data_json = json.dumps(data)

    # Send POST request
    url = f"{base_url}/batch-weight"
    response = requests.post(url, data=data_json, headers={
                             'Content-Type': 'application/json'})

    # Check if the request was successful (status code 200)
    assert response.status_code == 201

    # with app.app_context():
    #     # Check if the data was added to the database
    #     assert db.session.query(ContainersRegistered).filter_by(container_id="C-001").count() == 1
    #     assert db.session.query(ContainersRegistered).filter_by(container_id="C-002").count() == 1

    #     # Clean up the database after the test
    #     db.session.query(ContainersRegistered).filter_by(container_id="C-001").delete()
    #     db.session.query(ContainersRegistered).filter_by(container_id="C-002").delete()
    #     db.session.commit()


def test_get_unknown_containers_with_data(base_url):
    # Send a GET request to the route
    response = requests.get(f"{base_url}/unknown")

    # Check the response status code
    if response.text.strip() == "":
        # If the response content is empty, expect status code 400
        assert response.status_code == 404
    else:
        # Parse the response content as JSON
        data = response.json()
        # If it's a JSON list, expect status code 200
        assert isinstance(data, list)
        assert response.status_code == 200


base_url2 = 'http://localhost:5000'


def test_item_no_item_id1(client):
    response = requests.get(f"{base_url2}/item/")
    assert response.status_code == 404


def test_item_no_item_id2(client):
    pattern = r'.'
    response = requests.get(f"{base_url2}/item/{pattern}")
    assert response.status_code == 404


def test_invalid_item_id():
    response = requests.get(f"{base_url2}/item/invalid_id")
    assert response.status_code == 400


def test_invalid_custom_time():
    response = requests.get(
        f"{base_url2}/item/T-14732?from=20230101000000000000&to=202312312000035959")
    assert response.status_code == 422


def test_invalid_custom_time_2():
    id_pattern = r'^.{4,20}$'
    date_pattern = r'^\d{0,13}$'
    date_pattern_1 = r'^\d{15,20}$'

    response = requests.get(
        f"{base_url2}/item/{id_pattern}?from={date_pattern}&to={date_pattern_1}")
    assert response.status_code == 422


def test_valid_id_object_not_found():
    response = requests.get(f"{base_url2}/item/T-12345")
    assert response.status_code == 200


def test_session(client):
    response = requests.get(f"{base_url2}/session/")
    assert response.status_code == 404


def test_valid_item():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url2}/weight", json={
        "direction": "in",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "force": "true",
        "produce": "Apples"
    })
    assert r.status_code == 201
    r = r.json()
    response = requests.get(f"{base_url2}/item/T-{truck_id}")
    assert response.status_code == 200
    assert r['truck'] == f"T-{truck_id}"


def test_valid_item_2():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url2}/weight", json={
        "direction": "in",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "force": "true",
        "produce": "Apples"
    })
    assert r.status_code == 201
    r = r.json()
    response = requests.get(f"{base_url2}/item/T-{truck_id}")
    
    assert response.status_code == 200


# DIRECTIONS

def test_in_after_in_with_force():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url2}/weight", json={
        "direction": "in",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "force": True,
        "produce": "Apples"
    })
    assert r.status_code == 201
    r1 = requests.post(f"{base_url2}/weight", json={
        "direction": "in",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "force": True,
        "produce": "Apples"
    })
    assert r1.status_code == 201


def test_in_after_in_without_force():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url2}/weight", json={
        "direction": "in",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "produce": "Apples"
    })
    assert r.status_code == 400


def test_none_after_in_results_error():
    container_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url2}/weight", json={
        "direction": "none",
        "containers": f"C-{container_id}",
        "weight": random_weight,
        "unit": "kg",
        "produce": "Apples"
    })
    assert r.status_code == 400


def test_out_after_in_success():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r1 = requests.post(f"{base_url2}/weight", json={
        "direction": "in",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "force": True,
        "produce": "Apples"
    })
    assert r1.status_code == 201

    r = requests.post(f"{base_url2}/weight", json={
        "direction": "out",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "force": True,
        "produce": "Apples"
    })
    assert r.status_code == 201


def test_out_without_in_before_failure():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r1 = requests.post(f"{base_url2}/weight", json={
        "direction": "out",
        "truck": f"T-{truck_id}",
        "containers": "c1,c2",
        "weight": random_weight,
        "unit": "kg",
        "produce": "Apples"
    })
    assert r1.status_code == 400


def test_out_after_out_force_false():
    random_weight = random.randint(1, 1000)
    test_dict2 = {'direction': "out", 'truck': "T-12345",
                  'weight': random_weight, "unit": "kg", "produce": "Apples", "force": False}
    r1 = requests.post(f"{base_url2}/weight", json=test_dict2)
    assert r1.status_code == 400
    test_dict3 = {'direction': "out", 'truck': "T-12345",
                  'weight': random_weight, "unit": "kg", "produce": "Apples", "force": False}
    r2 = requests.post(f"{base_url2}/weight", json=test_dict3)
    assert r2.status_code == 400


def test_out_after_out_force_true():
    random_weight = random.randint(1, 1000)
    test_dict1 = {'direction': "in", 'truck': "T-12345",
                  'weight': random_weight, "unit": "kg", "produce": "Apples", "force": True}
    r1 = requests.post(f"{base_url2}/weight", json=test_dict1)
    assert r1.status_code == 500
    test_dict2 = {'direction': "out", 'truck': "T-12345",
                  'weight': random_weight, "unit": "kg", "produce": "Apples", "force": True}
    r2 = requests.post(f"{base_url2}/weight", json=test_dict2)
    assert r2.status_code == 201
    test_dict3 = {'direction': "out", 'truck': "T-12345",
                  'weight': random_weight, "unit": "kg", "produce": "Apples", "force": True}
    r3 = requests.post(f"{base_url2}/weight", json=test_dict3)
    assert r3.status_code == 201

    # WRONG_VALUES_IN


def test_out_after_out_force_true():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    test_dict1 = {'direction': "in", 'truck': f"T-{truck_id}"}
    r1 = requests.post(f"{base_url2}/weight", json=test_dict1)
    assert r1.status_code == 500
    test_dict1 = {'direction': "in",
                  'truck': f"T-{truck_id}", 'weight': random_weight}
    r1 = requests.post(f"{base_url2}/weight", json=test_dict1)
    assert r1.status_code == 500
    test_dict1 = {'direction': "in", 'truck': f"T-{truck_id}",
                  'weight': random_weight, "unit": "kg"}
    r1 = requests.post(f"{base_url2}/weight", json=test_dict1)
    assert r1.status_code == 500
    test_dict1 = {'direction': "in", 'truck': f"T-{truck_id}",
                  'weight': random_weight, "unit": "kg", "produce": "Apples"}
    r1 = requests.post(f"{base_url2}/weight", json=test_dict1)
    assert r1.status_code == 500


def test_no_product_name_results_succes():
    random_weight = random.randint(1, 1000)
    test_dict3 = {'direction': "out", 'truck': "T-12345",
                  'weight': random_weight, "unit": "kg", "force": True}
    r3 = requests.post(f"{base_url2}/weight", json=test_dict3)
    assert r3.status_code == 201
