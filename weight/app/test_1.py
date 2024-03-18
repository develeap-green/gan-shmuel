import pytest
from app import app
import requests
from random import sample
import string
import logging
import random


@pytest.fixture
def client():
    app.config.update({"TESTING": True})

    with app.test_client() as client:
        yield client


base_url = "http://localhost:5000"


def test_health_check(client):
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200


def test_item_no_item_id1(client):
    response = requests.get(f"{base_url}/item/")
    assert response.status_code == 404


def test_item_no_item_id2(client):
    pattern = r'.'
    response = requests.get(f"{base_url}/item/{pattern}")
    assert response.status_code == 404


def test_invalid_item_id():
    response = requests.get(f"{base_url}/item/invalid_id")
    assert response.status_code == 400


def test_invalid_custom_time():
    response = requests.get(
        f"{base_url}/item/T-14732?from=20230101000000000000&to=202312312000035959")
    assert response.status_code == 422


def test_invalid_custom_time_2():
    id_pattern = r'^.{4,20}$'
    date_pattern = r'^\d{0,13}$'
    date_pattern_1 = r'^\d{15,20}$'

    response = requests.get(
        f"{base_url}/item/{id_pattern}?from={date_pattern}&to={date_pattern_1}")
    assert response.status_code == 422


def test_valid_id_object_not_found():
    response = requests.get(f"{base_url}/item/T-12345")
    assert response.status_code == 200


def test_session(client):
    response = requests.get(f"{base_url}/session/")
    assert response.status_code == 404


def test_valid_item():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url}/weight", json={
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
    response = requests.get(f"{base_url}/item/T-{truck_id}")
    assert response.status_code == 200
    assert r['truck'] == f"T-{truck_id}"


def test_valid_item_2():
    truck_id = ''.join(sample(string.ascii_letters, 4))
    random_weight = random.randint(1, 1000)
    r = requests.post(f"{base_url}/weight", json={
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
    response = requests.get(f"{base_url}/item/T-{truck_id}")
    assert response.status_code == 200
