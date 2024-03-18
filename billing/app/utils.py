from app import app, db, DB_URI
from app.models import Provider, Rates, Trucks
from flask import abort, request, jsonify
from sqlalchemy import create_engine 
from datetime import datetime
import flask_excel as excel
import requests
import json
import pymysql
import logging
import os
import pandas as pd


#####################################
# For /tables route, testing only
from sqlalchemy import MetaData
########################################


# Configure logger
# logger = logging.getLogger(__name__)


# Utility function for the health-check route.
def checkDBHealth():
    try:
        with pymysql.connect(
            host='mysql-billing',
            user='user',
            password='pass',
            database='billing',
            port=3306,
            connect_timeout=5
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {"status": "OK"}
    except pymysql.MySQLError as e:
        # logger.error(f"Database health check failed: {e}")
        return {"status": "Failure", "reason": str(e)}


# Utility function for the tables route - testing only
def get_table_contents(table):
    try:
        records = db.session.query(table).all()
        return [str(record) for record in records]
    except Exception as e:
        # logger.error(f"Error retrieving table contents: {e}")
        return []
    
# For tables route
def showTablesContents():
    with app.app_context():
        meta = MetaData()
        meta.reflect(bind=db.engine)
        tables_contents = {}
        for table in meta.tables.values():
            table_name = table.name
            tables_contents[table_name] = get_table_contents(table)
        return jsonify(tables_contents)

    

# For bill route
def getRates():
    """
    Fetches rates from the database and returns a dictionary
    with product_id as keys and rate as values.
    """
    rates = Rates.query.all()
    return {rate.product_id: rate.rate for rate in rates}

def processWeightSessions(providerId, weightSessions):
    """
    Processes weight session data to calculate billing details.
    
    Args:
    - provider_id: Integer, ID of the provider to calculate billing.
    - weight_sessions: List of dictionaries, where each dictionary contains details
                       of a weight session including 'produce', 'neto' (net weight), etc.
    
    Returns:
    - A dictionary containing billing details including total amounts, counts,
      and payment for each product, along with overall totals.
    """
    rates = getRates()
    billDetails = {
        "provider_id": providerId,
        "products": {},
        "total": 0  # Total payment in agorot
    }
    
    # Iterate through each session to process billing
    for session in weightSessions:
        produce = session.get('produce')
        neto = session.get('neto', 0)

        # Skip if neto is not provided
        if neto == 0:
            continue
        
        rate = rates.get(produce, 0)  # Fetch the rate for the produce, default to 0 if not found
        
        # If the product is not already in the bill details, add it
        if produce not in billDetails['products']:
            billDetails['products'][produce] = {"count": 0, "amount": 0, "pay": 0}
        
        productDetails = billDetails['products'][produce]
        productDetails['count'] += 1
        productDetails['amount'] += neto
        productDetails['pay'] += neto * rate  
        
        # Update the total pay
        billDetails['total'] += neto * rate
    
    return billDetails


def fetchWeightSessions(from_date, to_date, provider_id):
    weightServerURL = os.getenv('WEIGHT_SERVER_URL')
    if not weightServerURL:
        raise ValueError("The WEIGHT_SERVER_URL environment variable must be set.")
    
    # Construct the URL with query parameters
    url = f"{weightServerURL}/weight?from={from_date}&to={to_date}&filter=in,out,none"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Assume the response is JSON
    except requests.RequestException as e:
        print(f"Error fetching weight sessions data: {e}")
        return None

###############################################################################################

# # Mock function to fetch weight sessions
# def fetchWeightSessions(fromDate, toDate, providerId):
#     # This function should interact with your database or external API
#     # to fetch weight sessions based on the provided arguments.
#     # Below is a placeholder implementation.
#     return [
#         {"truck": "T-001", "produce": "apple", "neto": 10},
#         {"truck": "T-002", "produce": "banana", "neto": 20},
#         {"truck": "T-001", "produce": "apple", "neto": 15},
#         {"truck": "T-003", "produce": "orange", "neto": 25},
#         {"truck": "T-002", "produce": "banana", "neto": 30}
#     ]
# def processWeightSessions(weightSessions, rates): 
#     billDetails = {
#         "products": {},
#         "total": 0
#     }
"""   
    for session in weightSessions:
        produce = session['produce']
        neto = session['neto']
        rate = rates.get(produce, 0)

        if produce not in billDetails['products']:
            billDetails['products'][produce] = {"count": 0, "amount": 0, "pay": 0}
        
        billDetails['products'][produce]['count'] += 1
        billDetails['products'][produce]['amount'] += neto
        billDetails['products'][produce]['pay'] += neto * rate

    billDetails['total'] = sum(product['pay'] for product in billDetails['products'].values())

    return billDetails
"""     
#############################################################################################################

def getTheBill(providerId):
    fromDate = request.args.get('from', datetime.now().strftime('%Y%m01000000'))
    toDate = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))
    weight_sessions = fetchWeightSessions(fromDate, toDate, providerId)

    if weight_sessions is None:
        return jsonify({'error': 'Failed to fetch weight sessions'}), 500

    rates = getRatesForTest()
    billDetails = processWeightSessions(weight_sessions, rates)

    return jsonify(billDetails)


def getRatesForTest():
    # Simulate fetching rates from the database
    return {"apple": 100, "banana": 150, "orange": 200}

#######################################################################################
def calculateTruckCount(weight_sessions):
    unique_trucks = set(session['truck'] for session in weight_sessions)
    return len(unique_trucks)
#####################################################################################

####################################################################################
def formatProductInfo(product, details):
    return {
        "product": product,
        "count": details['count'],
        "amount": details['amount'],
        "rate": details['rate'],
        "pay": details['pay']
    }
#################################################################################3

# For provider route
def createTheProvider():
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
        # logger.info(f"Error 400: {error_msg}")
        return jsonify({"Error": error_msg}), 400

    # Check if provider name exists, return 409 status code if it does.
    existingProvider = Provider.query.filter_by(name=name).first()

    if existingProvider:
        return jsonify({"Error": f"Provider {name} already exists."}), 409

    # Create a new provider after passing former tests
    newProvider = Provider(name=name)
    db.session.add(newProvider)
    db.session.commit()

    return jsonify({"Message": f"Provider {name} added successfully.", "id": newProvider.id}), 201

# For provider/<int:providerId> route
def updateTheProvider(providerId):
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
        # logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    provider = Provider.query.get(providerId)
    # If the provider does not exist, return a 404 Not Found error
    if provider is None:
        error_msg = f'Provider with id {providerId} does not exist.'
        # logger.info(f'Error 404: {error_msg}')
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


# For truck route
def createTheTruck():
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
        # logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    if data:
        providerId = data.get('provider_id')
        truckId = data.get('id')
    else:
        # Handle the case where data is None
        error_msg = 'No JSON data provided.'
        # logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    # Check if Truck name exists, return 409 status code if it does.
    existingTruck = Trucks.query.filter_by(id=truckId).first()
    if existingTruck:
        error_msg = f"Truck with license plate {truckId} already exists."
        # logger.info(f"Error 409: {error_msg}")
        return jsonify({"Error": error_msg}), 409

    provider = Provider.query.get(providerId)
    if provider is None:
        error_msg = f'Provider with ID {providerId} does not exist.'
        # logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    newTruck = Trucks(id=truckId, provider_id=providerId)
    db.session.add(newTruck)
    db.session.commit()

    return jsonify({"Success": f"Truck with license plate {truckId} registered successfully."}), 201


# For /truck/<string:truck_id> route 
def updateTheTruckProvider(truckID):
    """
        Update Truck Provider Route
        Updates the provider of an existing truck.
        Parameters:
            truckID (str): The unique identifier (license plate) of the truck to be updated.
        Returns:
            JSON: A success message indicating the truck provider update.
    """
    # Attempt to retrieve the 'provider_id' value from the JSON in the PUT request
    updateProviderId = request.json.get('provider_id', None)
    if updateProviderId is None:
        # If 'provider_id' is not provided or is empty, return a 400 Bad Request error
        error_msg = 'The provider_id field is required.'
        # logger.info(f'Error 400: {error_msg}')
        abort(400, error_msg)

    truck = Trucks.query.get(truckID)
    if truck is None:
        # If the truck does not exist, return a 404 Not Found error
        error_msg = f'Truck with id {truckID} does not exist.'
        # logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    provider = Provider.query.get(updateProviderId)
    if provider is None:
        # If the new provider does not exist, return a 404 Not Found error
        error_msg = f'Provider with id {updateProviderId} does not exist.'
        # logger.info(f'Error 404: {error_msg}')
        abort(404, error_msg)

    try:
        # Update the truck's provider_id with the new provider_id provided in the PUT request
        truck.provider_id = updateProviderId
        db.session.commit()  # Commit the transaction to save the changes in the database
        # Return a success message with a 200 OK status code
        return jsonify({'message': f'Truck {truckID} provider updated successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        error_msg = f'An error occurred: {str(e)}'
        # logger.error(f'Error 500: {error_msg}')
        abort(500, error_msg)


# For /truck/<id> route

####################################
# Mock trucks data file
with open('in/mock_trucks_with_sessions.json', 'r') as file:
    truckData = json.load(file) 
####################################       

def getTheTruck(id):
    # Remove whitespace and newlines from the truckID
    id = id.strip()

    truck = next((item for item in truckData if item['id'] == id), None)
    
    if truck:
        sessionIds = [session['id'] for session in truck['sessions']]
        return jsonify({
            "id": truck['id'],
            "tara": truck['tara'],
            "sessions": sessionIds
        })
    
    else:
        return jsonify({"error": f"Truck with id {id} not found."}), 404
    

# For rates route
def updateRatesFromFile():
    in_directory = os.path.abspath('in')
    file_path = os.path.join(in_directory, 'rates.csv')
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Read the Excel file into a DataFrame
            df = pd.read_csv(file_path)

            # Remove all existing rates from the database
            db.session.query(Rates).delete()
            
            # Add the database all rates from the file
            for _, row in df.iterrows():
                # Add new rate
                rate = Rates(product_id=row['product_id'], rate=row['rate'], scope=row['scope'])
                db.session.add(rate)
            
            # Commit the changes to the database
            db.session.commit()
            return "Database updated successfully"

        else:
            return "File does not exist"
    except Exception as e:
        # Rollback any changes made to the database session
        db.session.rollback()
        # Raise an HTTP 500 error with the exception message
        abort(500, f'An error occurred: {str(e)}')


def downloadRates():
    # Set up database connection based on DB_URI from __init__
    engine = create_engine(DB_URI)
    try:
        # Query the Rates table
        query = "SELECT * from Rates;"
        # Execute query with engine and store in DataFrame object df
        df = pd.read_sql(query, engine)
        # If the DataFrame is empty, return a 404 response
        if df.empty:
            return jsonify({"error": "No data available to download"}), 404
        # Convert DF to CSV, do not include DF column in the output
        response = df.to_csv(index=False)
        # Create a Flask response object and set the correct content type for CSV
        flaskResponse = pd.make_response(response)
        cd = 'attachment; filename=rates.csv'
        flaskResponse.headers['Content-Disposition'] = cd
        flaskResponse.mimetype='text/csv'
        return flaskResponse
    except Exception as e:
        # Log the exception and return an error response
        # app.logger.error(f"Error generating CSV file: {e}")
        return jsonify({"error": "Error generating CSV file"}), 500
    
