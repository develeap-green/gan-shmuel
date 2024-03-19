from http import HTTPStatus
import pytest
import json
from app import app, db, routes
import requests
from app.models import ContainersRegistered, Transactions



@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture       
def base_url():
    return "http://localhost:5000"

def test_retrieve_weight_list_success(base_url):
    url = f"{base_url}/weight?filter=in,out&from=20230101000000&to=20240101000000"
    response = requests.get(url)
    assert response.status_code == 200

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
    response = client.post('/batch-weight', data={'key':'value'})
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
    response = requests.post(url, data=data_json, headers={'Content-Type': 'application/json'})
    
    # Check if the request was successful (status code 200)
    assert response.status_code == 200

    # with app.app_context():
    #     # Check if the data was added to the database
    #     assert db.session.query(ContainersRegistered).filter_by(container_id="C-001").count() == 1
    #     assert db.session.query(ContainersRegistered).filter_by(container_id="C-002").count() == 1

    #     # Clean up the database after the test
    #     db.session.query(ContainersRegistered).filter_by(container_id="C-001").delete()
    #     db.session.query(ContainersRegistered).filter_by(container_id="C-002").delete()
    #     db.session.commit()
