import requests
import random
import time

BASE_URL = "http://localhost:5000"

def get_short_timestamp():
    return str(int(time.time()))[-4:]

def generate_provider_name():
    random_part = random.randint(10, 99)
    timestamp = get_short_timestamp()
    return f"Provider_{timestamp}_{random_part}"

def generate_truck_id():
    random_part = random.randint(10000, 99999)
    timestamp = get_short_timestamp()
    return f"T-{timestamp}-{random_part}"[:10]


GLOBAL_UNIQUE_PROVIDER_NAME = generate_provider_name()
GLOBAL_PROVIDER_ID = None
GLOBAL_TRUCK_ID = generate_truck_id()

def setup_module(module):
    """Setup for the entire module - Create provider and truck"""
    global GLOBAL_PROVIDER_ID, GLOBAL_TRUCK_ID

    provider_data = {"name": GLOBAL_UNIQUE_PROVIDER_NAME}
    provider_response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    assert provider_response.status_code == 201, "Failed to create global provider"
    GLOBAL_PROVIDER_ID = provider_response.json().get("id")

    truck_data = {"provider_id": GLOBAL_PROVIDER_ID, "id": GLOBAL_TRUCK_ID}
    truck_response = requests.post(f"{BASE_URL}/truck", json=truck_data)
    assert truck_response.status_code == 201, "Failed to create global truck"


def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()['Status'] == 'OK'


def test_create_provider_duplicate():
    provider_data = {"name": GLOBAL_UNIQUE_PROVIDER_NAME}
    response = requests.post(f"{BASE_URL}/provider", json=provider_data)
    assert response.status_code == 409, "Duplicate provider creation should fail but didn't."


def test_update_provider():
    update_data = {"name": "Updated " + GLOBAL_UNIQUE_PROVIDER_NAME}
    response = requests.put(f"{BASE_URL}/provider/{GLOBAL_PROVIDER_ID}", json=update_data)
    assert response.status_code == 200, "Failed to update provider"

def test_update_nonexistent_provider():
    update_data = {"name": "Nonexistent Provider"}
    response = requests.put(f"{BASE_URL}/provider/99999", json=update_data)
    assert response.status_code == 404, "Updating a nonexistent provider should return 404"


def test_create_duplicate_truck():
    truck_data = {"provider_id": GLOBAL_PROVIDER_ID, "id": GLOBAL_TRUCK_ID}
    response = requests.post(f"{BASE_URL}/truck", json=truck_data)
    assert response.status_code == 409, f"Truck should already exist. Response: {response.text}"

def test_update_truck():
    update_data = {"provider_id": GLOBAL_PROVIDER_ID}
    response = requests.put(f"{BASE_URL}/truck/{GLOBAL_TRUCK_ID}", json=update_data)
    assert response.status_code == 200, "Failed to update truck"

# Not working until Zori fixes the trucks-using-DB instead of mock
# def test_get_truck_data():
#     response = requests.get(f"{BASE_URL}/truck/{GLOBAL_TRUCK_ID}")
#     assert response.status_code == 200, "Expected to find the global truck data"

def test_post_rates():
    url = f"{BASE_URL}/rates"
    with open('in/rates.csv', 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
    assert response.status_code == 200, "Failed to upload rates"

def test_get_rates():
    test_post_rates()  # Ensure there are rates to download by first posting rates
    get_url = f"{BASE_URL}/rates"
    get_response = requests.get(get_url)
    assert get_response.status_code == 200, "Failed to download rates"

def test_get_rates_with_date_range():
    test_post_rates()
    url = f"{BASE_URL}/rates?from=20230101&to=20240101"
    response = requests.get(url)
    assert response.status_code == 200, "Should succeed with valid date range"


if __name__ == "__main__":
    setup_module(None)