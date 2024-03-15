from flask import abort, request, jsonify
from app import app, db
from app.health import check_app_health, check_db_health
from app.models import Provider


# Root route for testing purposes
@app.route('/')
def root():
    return jsonify({'message': 'Welcome to the Billing API'}), 200

# Moved the provider.midel to models.py


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
        db.session.rollback()  # Roll back the transaction in case of error
        # Then, return a 500 Internal Server Error with the error message
        abort(500, f'An error occurred: {str(e)}')


# Check if DB healthy - commented for now, added a healthcheck for flask&db containers
# def checkResource(resource):
#     try:
#         # Check the resource status and parse it status code (int)
#         response = requests.get(resource).status_code
#         if response == 200:
#             return "OK"
#         else:
#             return "Failure"
#     # Error raise when domain not found
#     except requests.RequestException:
#         return "Failure"


# # Health check route
# @app.route("/health",methods=["GET"])
# def health_check():
#     resourceStatus = checkResource(resource) # Call checkResource function and check status
#     if request.method == "GET" and resourceStatus == "OK": # if resource found
#         return {"status": "OK", "statusCode": "200 OK", }
#     else: # if resource not found or not good
#         return {"status": "Failure", "statusCode": "500 Internal Server Error"}

# Health check route using functions from health.py to save space here
@app.route("/health", methods=["GET"])
def health_check():
    app_health = check_app_health()
    db_health = check_db_health()

    if app_health["status"] == db_health["status"] == "OK":
        return jsonify({"status": "OK"}), 200
    else:
        return jsonify({
            "status": "Failure",
            "details": {
                "app_health": app_health,
                "db_health": db_health
            }
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
