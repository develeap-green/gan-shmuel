import json
from flask import abort, request, jsonify
from app import app, db
from app.utils import check_db_health, get_table_contents
from app.models import Provider, Rates, Trucks

# For /tables route, testing only
from sqlalchemy import MetaData

# Root route for testing purposes
@app.route('/')
def root():
    return jsonify({'message': 'Welcome to the Billing API'}), 200


# Route to create a provider
@app.route('/provider', methods=["POST"])
def createProvider():
    # Store the provider POST request
    requestData = request.get_json()

    # Return 400 error if no name is given in the request. 
    # Check for empty or whitespace only string.
    name = requestData.get("name", "").strip()
    if not name:
        return jsonify({"error": "Missing name in request or name is empty."}), 400

    # Check if provider name exists, return 409 status code if it does.
    existingProvider = Provider.query.filter_by(name=name).first()
    if existingProvider:
        return jsonify({"Error": f"Provider {name} already exists."}), 409

    newProvider = Provider(name=name)
    db.session.add(newProvider)
    db.session.commit()

    return jsonify({"message": f"Provider {name} with ID {newProvider.id} added successfully."}), 201


# Route to update a provider
@app.route('/provider/<int:providerId>', methods=['PUT'])
def updateProvider(providerId):

    # Attempt to retrieve the 'name' value from the JSON in the PUT request
    updateName = request.json.get('name', None)
    if not updateName:
        # If 'name' is not provided or is empty, return a 400 Bad Request error
        abort(400, 'The name field is required.')

    # Find the provider by ID
    provider = Provider.query.get(providerId)
    # If the provider does not exist, return a 404 Not Found error
    if provider is None:
        abort(404, f'Provider with id {providerId} does not exist.')

    try:
        # Update the provider's name with the new name provided in the PUT request
        provider.name = updateName
        db.session.commit()  # Commit the transaction to save the changes in the database
        # Return a success message with a 200 OK status code
        return jsonify({'message': 'Provider updated successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        abort(500, f'An error occurred: {str(e)}')



# Route to create a provider
@app.route('/truck', methods=["POST"])
def createTruck():
    # Store the Truck POST request
    data = request.get_json(silent=True)
   # If 'newTruck' is not provided or is empty, return a 400 Bad Request error
    if not data or 'provider_id' not in data or 'id' not in data:  
        abort(400, 'The truck field is required.')

    if data:
        providerId = data.get('provider_id')
        truckId = data.get('id')
    else:
    # Handle the case where data is None
        abort(400, 'No JSON data provided.')

    # Check if Truck name exists, return 409 status code if it does.
    existingTruck = Trucks.query.filter_by(id=truckId).first()
    if existingTruck:
        return jsonify({"Error": f"Truck with license plate {truckId} already exists."}), 409

    provider = Provider.query.get(providerId)
    if provider is None:
        abort(404, f'Provider with ID {providerId} does not exist.')

    newTruck = Trucks(id=truckId, provider_id=providerId)
    db.session.add(newTruck)
    db.session.commit()

    return jsonify({"Success": f"Truck with license plate {truckId} registered successfully."}), 201

# Route to update a truck
@app.route('/truck/<string:truck_id>/', methods=['PUT'])
def updateTruckProvider(truck_id):
    # Attempt to retrieve the 'provider_id' value from the JSON in the PUT request
    updateProviderId = request.json.get('provider_id', None)
    if updateProviderId is None:
        # If 'provider_id' is not provided or is empty, return a 400 Bad Request error
        abort(400, 'The provider_id field is required.')

    # Find the truck by ID
    truck = Trucks.query.get(truck_id)
    if truck is None:
        # If the truck does not exist, return a 404 Not Found error
        abort(404, f'Truck with id {truck_id} does not exist.')

    # Check if the new provider exists
    provider = Provider.query.get(updateProviderId)
    if provider is None:
        # If the new provider does not exist, return a 404 Not Found error
        abort(404, f'Provider with id {updateProviderId} does not exist.')

    try:
        # Update the truck's provider_id with the new provider_id provided in the PUT request
        truck.provider_id = updateProviderId
        db.session.commit()  # Commit the transaction to save the changes in the database
        # Return a success message with a 200 OK status code
        return jsonify({'message': f'Truck {truck_id} provider updated successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        # If an error occurs, return a 500 Internal Server Error
        abort(500, f'An error occurred: {str(e)}')


# Mock trucks data file
with open('../mock_trucks_with_sessions.json', 'r') as file:
    truckData = json.load(file)
    
# Route to get truck data by id
# Display truck id, last known tara in kg and sessions
@app.route('/truck/<id>', methods=['GET'])
def getTruck(id):

    # Remove whitespace and newlines from the truck_id
    id = id.strip()

    truck = next((item for item in truckData if item['id'] == id), None)
    
    if truck:
        return jsonify({
            "id": truck['id'],
            "tara": truck['tara'],
            "sessions": truck['sessions']
        })
    
    else:
        return jsonify({"error": f"Truck with id {id} not found."}), 404
# GET /truck/<id>?from=t1&to=t2
# - id is the truck license. 404 will be returned if non-existent
# - t1,t2 - date-time stamps, formatted as yyyymmddhhmmss. server time is assumed.
# default t1 is "1st of month at 000000". default t2 is "now".
# Returns a json:
# { "id": <str>,
#   "tara": <int>, // last known tara in kg
#   "sessions": [ <id1>,...]
# }

# Health check route using function from health.py
@app.route("/health", methods=["GET"])
def health_check():
    db_health = check_db_health()

    if db_health["status"] == "OK":
        return jsonify({"status": "OK"}), 200
    else:
        return jsonify({"status": "Failure", "details": {"db_health": db_health}}), 500

#  Route to see the contents of all DB tables for testing
@app.route('/tables', methods=['GET'])
def show_tables_and_contents():
    with app.app_context():
        meta = MetaData()
        meta.reflect(bind=db.engine)
        tables_contents = {}
        for table in meta.tables.values():
            table_name = table.name
            tables_contents[table_name] = get_table_contents(table)
        return jsonify(tables_contents)


if __name__ == "__main__":
    app.run(debug=True)

