from app import app, db, DB_URI
from app.models import Provider, Rates, Trucks
from flask import abort, request, jsonify, make_response
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
def processWeightSessions(weightSessions, rates):
    """Process each weight session to calculate the total bill and count unique trucks."""
    # Initialize bill details with empty products dictionary and total bill as 0
    billDetails = {"products": {}, "total": 0}
    unique_trucks = set()  # Initialize a set to count unique trucks
    # Iterate over each weight session
    for session in weightSessions:
        produce = session['produce']  # Get the product from the session
        neto = session['neto']  # Get the neto weight from the session
        truck = session['truck']  # Get the truck ID from the session
        # Ensure this rate lookup aligns with how rates are keyed in the dictionary.
        rate = rates[produce]  # Get the rate for the product from the rates dictionary
        # Debugging print to check rate applied for each product
        print(f"{produce}: Rate applied - {rate}, Neto - {neto}")
        unique_trucks.add(truck)  # Add truck to the set of unique trucks
        # If product not in billDetails, add it with initial count, amount, rate, and pay
        if produce not in billDetails['products']:
            billDetails['products'][produce] = {
                "count": 1,
                "amount": neto,
                "rate": rate,
                "pay": neto * rate
            }
        else:
            # If product already exists, update count, amount, and recalculate pay
            productDetails = billDetails['products'][produce]
            productDetails['count'] += 1
            productDetails['amount'] += neto
            productDetails['pay'] = productDetails['amount'] * rate  # Recalculate pay based on updated amount
    # After updating product details, calculate the total pay by summing pay for all products
    billDetails['total'] = sum(product['pay'] for product in billDetails['products'].values())
    # Update the count of unique trucks in billDetails
    billDetails['truck_count'] = len(unique_trucks)
    return billDetails
# def fetch_weight_sessions(from_date, to_date, provider_id):
#     # Get the weight server URL from environment variables
#     weight_server_url = os.getenv('WEIGHT_SERVER_URL')
#     if not weight_server_url:
#         # Raise an error if the WEIGHT_SERVER_URL environment variable is not set
#         raise ValueError("The WEIGHT_SERVER_URL environment variable must be set.")
#     # Construct the URL with query parameters
#     url = f"{weight_server_url}/weight?from={from_date}&to={to_date}&filter=in,out,none"
#     try:
#         # Send a GET request to the constructed URL
#         response = requests.get(url)
#         response.raise_for_status()  # Check for HTTP errors
#         return response.json()  # Assume the response is JSON
#     except requests.RequestException as e:
#         # Handle any request exceptions, such as network errors
#         print(f"Error fetching weight sessions data: {e}")
#         return None
# # Mock function to simulate fetching weight sessions from a database
def fetchWeightSessions(from_date, to_date, provider_id):
    #  sample data resembling database records
    sample_data = [
        {"datetime": "2024-03-11 12:38:38", "direction": "out", "truck": "T-18186", "produce": "Navel", "neto": 700, "session_id": 7781},
        {"datetime": "2024-03-15 17:07:42", "direction": "in", "truck": "T-15083", "produce": "Blood", "neto": 847, "session_id": 8119},
        {"datetime": "2024-03-10 23:13:05", "direction": "out", "truck": "T-54612", "produce": "Grapefruit", "neto": 792, "session_id": 8621},
        {"datetime": "2024-03-08 10:24:55", "direction": "in", "truck": "T-17464", "produce": "Valencia", "neto": 1507, "session_id": 4943}
    ]
    # Remove newline character and parse dates
    from_date_cleaned = from_date.strip()  # Remove  whitespace and newline characters
    to_date_cleaned = to_date.strip()  # Remove  whitespace and newline characters
    # Convert from_date and to_date strings to datetime objects
    from_date_obj = datetime.strptime(from_date_cleaned, '%Y%m%d%H%M%S')
    to_date_obj = datetime.strptime(to_date_cleaned, '%Y%m%d%H%M%S')
    # Filter the sample data based on the provided date range and provider_id (if applicable)
    filtered_data = [record for record in sample_data if from_date_obj <= datetime.strptime(record["datetime"], '%Y-%m-%d %H:%M:%S') <= to_date_obj]
    return filtered_data
# Function to fetch rates from a CSV file and return them as a dictionary
def getRatesDict(providerID):
    try:
        ratesDict = {}
        # Query the DB for all rates
        allRatesList = Rates.query.all()
        # Filter the relevant products by provider
        for record in allRatesList:
            product_id = record.product_id
            rate = record.rate
            scope = record.scope
            # Check if the scope matches 'All' or the specific provider_id
            if scope == 'All' or scope == str(providerID):
                # Add the product_id and rate to the ratesDict
                ratesDict[product_id] = float(rate)
        # Print a message if no rates are found in the CSV file
        if not ratesDict:
            print("No rates found. Check CSV file content or query.")
        else:
            # Print the fetched rates if rates are found
            print("Fetched rates:", ratesDict)
        return ratesDict
    except Exception as e:
        # Print an exception message if there's an error fetching rates
        print(f"Exception fetching rates: {e}")
        return {}
def getTheBill(providerId):
    # Get the 'from' and 'to' date parameters from the request, defaulting to the current date and time if not provided
    fromDate = request.args.get('from', datetime.now().strftime('%Y%m01000000'))
    toDate = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))
    # Fetch weight sessions data based on the provided date range and providerId
    providers = Trucks.query.filter_by(provider_id=providerId).all()
    provider_ids = [provider.provider_id for provider in providers]
    if providerId not in provider_ids:
        return jsonify({'error': 'no trucks for this provider'}), 400
    weight_sessions = fetchWeightSessions(fromDate, toDate, providerId)
    # If weight_sessions is None (indicating a failure to fetch), return an error response
    if weight_sessions is None:
        return jsonify({'error': 'Failed to fetch weight sessions'}), 500
    # Fetch rates for the providerId
    rates_dict = getRatesDict(providerId)
    # If rates_dict is empty (indicating a failure to fetch rates), return an error response
    if not rates_dict:
        return jsonify({'error': 'Failed to fetch rates'}), 500
    # Process weight sessions and rates to calculate bill details
    billDetails = processWeightSessions(weight_sessions, rates_dict)
    # Return the calculated bill details as a JSON response
    return jsonify(billDetails)

########
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
        flaskResponse = make_response(response)
        cd = 'attachment; filename=rates.csv'
        flaskResponse.headers['Content-Disposition'] = cd
        flaskResponse.mimetype='text/csv'
        return flaskResponse
    except Exception as e:
        # Log the exception and return an error response
        # app.logger.error(f"Error generating CSV file: {e}")
        return jsonify({"error": "Error generating CSV file"}), 500
    
