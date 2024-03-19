from http import HTTPStatus
from sqlalchemy import text
from app.utils import showTablesContents, downloadRates, updateRatesFromFile, getTheBill, \
      createTheProvider, updateTheProvider, createTheTruck, updateTheTruckProvider, getTheTruck
from flask import request, jsonify
from app import app, db
import os
#import logging

##################################
# Retrieve the WEIGHT_SERVER_URL environment variable from docker compose 
weight_server_url = os.getenv('WEIGHT_SERVER_URL')
# Check if the WEIGHT_SERVER_URL environment variable is not set
if not weight_server_url:
   raise ValueError("The WEIGHT_SERVER_URL environment variable must be set.")
#####################################

#######################################################
# Get the logger object configured in init.py
#logger = logging.getLogger(__name__)
####################################################3

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
    return getTheTruck(id)


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
#####################################################################
    

# Post= upload new rates , Get= download a file of the rates
@app.route("/rates", methods=["POST", "GET"])
def updateRates():
    if request.method == "POST":
        return updateRatesFromFile()
    elif request.method == "GET":
        return downloadRates()


if __name__ == "__main__":
    app.run(debug=True)

