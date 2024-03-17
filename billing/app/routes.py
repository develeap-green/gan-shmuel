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

    # Attempt to retrieve the 'name' value from the JSON payload in the PUT request
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
@app.route('/truck/', methods=["POST"])
def createTruck():
    # Store the Truck POST request
    data = request.json.get('provider_id', None)

   # If 'newTruck' is not provided or is empty, return a 400 Bad Request error
    if not data or 'provider_id' not in data:
        abort(400, 'The truck field is required.')

    providerId = data.get('provider')
    truck_id = data.get('id')

    if not providerId or not truck_id:
        abort(400, 'The provider and id fields are required.')

    # Check if Truck name exists, return 409 status code if it does.
    existingTruck = Trucks.query.filter_by(id=truck_id).first()
    if existingTruck:
        return jsonify({"Error": f"Truck with license plate {truck_id} already exists."}), 409

    newTruck = Trucks(id=truck_id, provider_id=providerId)
    db.session.add(newTruck)
    db.session.commit()

    return jsonify({"Success": f"Truck with license plate {truck_id} registered successfully."}), 201
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

