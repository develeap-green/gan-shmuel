from flask import abort, request, jsonify
from app import app, db, Flask
from flask_sqlalchemy import SQLAlchemy
import requests


# Check if we are in a testing environment
# Use an SQL in-memory database for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


#  MySQL for development/production
# app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy extension with the Flask app
db = SQLAlchemy(app)


# Root route for testing purposes
@app.route('/')
def root():
    return "jsonify({'message': 'Welcome to the Billing API'}), 200"


# # Define the Provider model
class Provider(db.Model):
    __tablename__ = 'Provider'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


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
    except Exception as err:
        db.session.rollback()  # Roll back the transaction in case of error
        # Then, return a 500 Internal Server Error with the error message
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
    if request.method == "GET" and resourceStatus == "OK": # if resource found
        return {"status": "OK", "statusCode": "200 OK", }
    else: # if resource not found or not good
        return {"status": "Failure", "statusCode": "500 Internal Server Error"}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
