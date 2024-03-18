import json
from flask import abort, request, jsonify
from app import app, db
from app.utils import check_db_health, get_table_contents
from app.models import Provider, Rates, Trucks
import logging

# For /tables route, testing only
from sqlalchemy import MetaData

# Get the logger object configured in init.py
logger = logging.getLogger(__name__)


@app.route('/')
def root():
    return jsonify({'message': 'Welcome to the Billing API'}), 200


@app.route('/provider', methods=["POST"])
def createProvider():
    """
       Create Provider Route
       Creates a new provider record based on the provided name.
       Request JSON Structure:
           {
               "name": "Provider Name"
           }
       Returns:
           JSON: A success message along with the unique provider ID.
    """
    # Store the provider POST request
    requestData = request.json

    # Return 400 error if no name is given in the request. 
    # Check for empty or whitespace only string.
    name = requestData.get("name", "").strip()
    if not name:
        error_msg = "Missing or empty 'name' field in the request."
        logger.info(f"Error 400: {error_msg}")
        return jsonify({"Error": error_msg}), 400

    # Check if provider name exists, return 409 status code if it does.
    existingProvider = Provider.query.filter_by(name=name).first()

    if existingProvider:
        return jsonify({"Error": f"Provider {name} already exists."}), 409

    newProvider = Provider(name=name)
    db.session.add(newProvider)
    db.session.commit()

    return jsonify({"Message": f"Provider {name} added successfully.", "id": newProvider.id}), 201


@app.route('/provider/<int:providerId>', methods=['PUT'])
def updateProvider(providerId):
    """
        Update Provider Route
        Updates the name of an existing provider.
        Parameters:
            providerId (int): The unique identifier of the provider to be updated.
        Returns:
            JSON: A success message indicating the provider update.
    """
    # Attempt to retrieve the 'name' value from the JSON in the PUT request
    updateName = request.json.get('name', None)
    if not updateName:
        # If 'name' is not provided or is empty, return a 400 Bad Request error
        error_msg = 'Missing or empty "name" field in the request.'
        logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    provider = Provider.query.get(providerId)
    # If the provider does not exist, return a 404 Not Found error
    if provider is None:
        error_msg = f'Provider with id {providerId} does not exist.'
        logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    try:
        # Update the provider's name with the new name provided in the PUT request
        provider.name = updateName
        db.session.commit()  # Commit the transaction to save the changes in the database
        # Return a success message with a 200 OK status code
        return jsonify({'Message': 'Provider updated successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        abort(500, f'An error occurred: {str(e)}')


@app.route('/truck', methods=["POST"])
def createTruck():
    """
        Create Truck Route
        Registers a new truck in the system.
        Request JSON Structure:
            {
                "provider_id": 123,
                "id": "ABC123"
            }
        Returns:
            JSON: A success message indicating the successful registration of the truck.
    """
    # Store the Truck POST request
    data = request.json
    # If 'newTruck' is not provided or is empty, return a 400 Bad Request error
    if not data or 'provider_id' not in data or 'id' not in data:  
        error_msg = 'The "provider_id" and "truck id" fields are required.'
        logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    if data:
        providerId = data.get('provider_id')
        truckId = data.get('id')
    else:
        # Handle the case where data is None
        error_msg = 'No JSON data provided.'
        logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    # Check if Truck name exists, return 409 status code if it does.
    existingTruck = Trucks.query.filter_by(id=truckId).first()
    if existingTruck:
        error_msg = f"Truck with license plate {truckId} already exists."
        logger.info(f"Error 409: {error_msg}")
        return jsonify({"Error": error_msg}), 409

    provider = Provider.query.get(providerId)
    if provider is None:
        error_msg = f'Provider with ID {providerId} does not exist.'
        logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    newTruck = Trucks(id=truckId, provider_id=providerId)
    db.session.add(newTruck)
    db.session.commit()

    return jsonify({"Success": f"Truck with license plate {truckId} registered successfully."}), 201


@app.route('/truck/<string:truck_id>/', methods=['PUT'])
def updateTruckProvider(truck_id):
    """
        Update Truck Provider Route
        Updates the provider of an existing truck.
        Parameters:
            truck_id (str): The unique identifier (license plate) of the truck to be updated.
        Returns:
            JSON: A success message indicating the truck provider update.
    """
    # Attempt to retrieve the 'provider_id' value from the JSON in the PUT request
    updateProviderId = request.json.get('provider_id', None)
    if updateProviderId is None:
        # If 'provider_id' is not provided or is empty, return a 400 Bad Request error
        error_msg = 'The provider_id field is required.'
        logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    truck = Trucks.query.get(truck_id)
    if truck is None:
        # If the truck does not exist, return a 404 Not Found error
        error_msg = f'Truck with id {truck_id} does not exist.'
        logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    provider = Provider.query.get(updateProviderId)
    if provider is None:
        # If the new provider does not exist, return a 404 Not Found error
        error_msg = f'Provider with id {updateProviderId} does not exist.'
        logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    try:
        # Update the truck's provider_id with the new provider_id provided in the PUT request
        truck.provider_id = updateProviderId
        db.session.commit()  # Commit the transaction to save the changes in the database
        # Return a success message with a 200 OK status code
        return jsonify({'message': f'Truck {truck_id} provider updated successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        error_msg = f'An error occurred: {str(e)}'
        logger.error(f'Error 500: {error_msg}')
        abort(500, error_msg)


# Mock trucks data file
with open('in/mock_trucks_with_sessions.json', 'r') as file:
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

@app.route("/health", methods=["GET"])
def health_check():
    """
        Health Check Route
        Performs a health check on the system, verifying the availability of external resources.
        Returns:
            JSON: A status message indicating the health status of the system.
    """
    db_health = check_db_health()

    if db_health["status"] == "OK":
        return jsonify({"Status": "OK"}), 200
    else:
        return jsonify({"Status": "Failure", "details": {"db_health": db_health}}), 500


@app.route('/tables', methods=['GET'])
def show_tables_and_contents():
    """
        Show Tables and Contents Route (For Testing)
        Retrieves the contents of all database tables for testing purposes.
        Returns:
            JSON: Contents of all database tables.
    """
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

