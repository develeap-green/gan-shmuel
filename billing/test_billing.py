import requests
import random

BASE_URL = "http://localhost:5000"

def generate_provider_name():
    return f"Provider {random.randint(10, 99)}"

def generate_product_id():
    products = ["Navel", "Blood", "Mandarin", "Shamuti", "Tangerine", "Clementine", "Grapefruit", "Valencia"]
    product = random.choice(products)
    return f"{product}-{random.randint(100, 999)}"

def generate_truck_id():
    return f"T-{random.randint(10000, 99999)}"

def test_index_page():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Welcome to the Billing API" in response.text

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()['Status'] == 'OK'

def test_create_provider():
    provider_name = generate_provider_name()
    provider_data = {"name": provider_name}
    response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    assert response.status_code == 201
    assert f"Provider {provider_name} added successfully." in response.text

def test_create_provider_duplicate():
    provider_name = generate_provider_name()
    provider_data = {"name": provider_name}
    # First creation should succeed
    response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    assert response.status_code == 201
    # Second creation with the same name should fail
    response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    assert response.status_code == 409

def test_create_truck():
    truck_id = generate_truck_id()
    provider_data = {"name": generate_provider_name()}
    response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    provider_id = response.json().get("id")
    truck_data = {"provider_id": provider_id, "id": truck_id}
    response = requests.post(f"{BASE_URL}/truck", json=truck_data)
    assert response.status_code == 201
    assert f"Truck with license plate {truck_id} registered successfully." in response.text

def test_update_provider():
    provider_name = generate_provider_name()
    provider_data = {"name": provider_name}
    response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    provider_id = response.json().get("id")
    update_data = {"name": "Updated " + provider_name}
    response = requests.put(f"{BASE_URL}/provider/{provider_id}", json=update_data)
    assert response.status_code == 200
    assert "Provider updated successfully." in response.text

def test_update_nonexistent_provider():
    update_data = {"name": "Nonexistent Provider"}
    response = requests.put(f"{BASE_URL}/provider/99999", json=update_data)
    assert response.status_code == 404

def test_get_truck_data():
    truck_id = generate_truck_id()
    response = requests.get(f"{BASE_URL}/truck/{truck_id}")
    assert response.status_code == 404  # Assuming truck doesn't exist

