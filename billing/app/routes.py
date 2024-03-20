from http import HTTPStatus
from sqlalchemy import text
from app.utils import showTablesContents, downloadRates, updateRatesFromFile, getTheBill, \
      createTheProvider, updateTheProvider, createTheTruck, updateTheTruckProvider, getTheTruck
from flask import request, jsonify
from app import app, db
import datetime
import requests
#import logging

#logger = logging.getLogger(__name__)

@app.route('/')
def root():
    return jsonify({'message': 'Welcome to the Billing API'}), 200


# Creates a new provider record
@app.route('/provider', methods=["POST"])
def createProvider():
    return createTheProvider()


# Update provider name
@app.route('/provider/<int:providerId>', methods=['PUT'])
def updateProvider(providerId):
    return updateTheProvider(providerId)


# Registers a truck in the system
@app.route('/truck', methods=["POST"])
def createTruck():
    return createTheTruck()


# Update provider id
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
    return updateTheTruckProvider(truck_id)


# Route to get truck data by id
# Display truck id, last known tara in kg and sessions
@app.route('/truck/<id>', methods=['GET'])
def getTruck(id):
    # if not id.startswith("T-"):
    #     return jsonify({"error": "Not a truck ID."})
    fromDate = request.args.get('from', datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime('%Y%m%d%H%M%S'))
    toDate = request.args.get('to', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    # URL for API endpoint
    url = f"http://greenteam.hopto.org:8081/item/{id}?from={fromDate}&to={toDate}"
    # Get requests for the endpoint
    response = requests.get(url)
    # If request is OK
    if response.status_code == 200:
        # Parse to JSON
        truckData = response.json()
        # If parse successful
        if truckData:
            # Get all session ID's for a truck
            sessionsIds = [session['id'] for session in truckData.get('sessions', [])]
            # Return the relevant data as JSON
            return jsonify({
                "id": truckData.get('id'),
                "tara": truckData.get('tara'),
                "sessions": sessionsIds
            })
    # Return 404 if not found
    else:
        return jsonify({"error": f"Truck with id {id} not found."}), 404


# Get the bill
@app.route('/bill/<int:providerId>', methods=['GET'])
def getBill(providerId):
    return getTheBill(providerId)


# Health Check Route
@app.route("/health", methods=["GET"])
def health_check():
    """
    Health Check Route
    Performs a health check on the system, verifying the availability of external resources.
    Returns:
        JSON: A status message indicating the health status of the system.
    """
    try:
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return jsonify({"Status": "OK"}), HTTPStatus.OK
    except Exception as e:
        # logging.error(f"Database health check failed: {e}")
        return jsonify({"Status": "Failure", "reason": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


####################################################################
# Show the tables inside the DB - FOR TEST PURPOSES
@app.route('/tables', methods=['GET'])
def showTablesAndContents():
    """
        Show Tables and Contents Route (For Testing)
        Retrieves the contents of all database tables for testing purposes.
        Returns:
            JSON: Contents of all database tables.
    """
    return showTablesContents()


# Post= upload new rates , Get= download a file of the rates
@app.route("/rates", methods=["POST", "GET"])
def updateRates():
    if request.method == "POST":
        return updateRatesFromFile()
    elif request.method == "GET":
        return downloadRates()


if __name__ == "__main__":
    app.run(debug=True)

