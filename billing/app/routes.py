from app import app

from flask import Flask, abort, request, jsonify
from flask_mysqldb import MySQL
import requests

app = Flask(__name__)


@app.route('/provider/<providerId>', methods=['PUT'])
def updateProvider(providerId):
    cur = MySQL.connection.cursor()
    updateName = request.json.get('name', None)
    if updateName is None or updateName == '':
        abort(400, 'The name field is required.')
    
    existing_provider = cur.execute('SELECT id FROM Provider WHERE id = %s', (providerId,))
    existing_provider = cur.fetchone()

    if not existing_provider:
        abort(404, f'Provider with id {providerId} does not exist.')

    try:
        cur.execute('UPDATE Provider SET name = %s WHERE id = %s', (updateName, providerId))
        return jsonify({'message': 'Provider updated successfully.'}), 200
    except Exception as err:
        abort(500, f'An error occurred: {str(err)}')



# Until we get db name / ip that for testing
#resource = "http://127.0.0.1:5000/health"
#resource = "https://www.goofhjjstgle.com/"
resource = "https://www.google.com/"

# Check if DB healthy
def checkResource(resource):
    try:
        # Check the resource status and parse it status code (int)
        response = requests.get(resource).status_code
        if response == 200:
            return "OK"
        else:
            return "Failure"
    # Error raise when domain not found
    except requests.RequestException:
        return "Failure"

# Get request check if db is up
@app.route("/health",methods=["GET"])
def health_check():
    resourceStatus = checkResource(resource) # Call checkResource function and check status
    if request.method == "GET" and resourceStatus == "OK": #if resource found
        return {"status": "OK", "statusCode": "200 OK", }
    else: #if resource not found or not good
        return {"status": "Failure", "statusCode": "500 Internal Server Error"}

    
if __name__ == "__main__":
    app.run(debug=True)