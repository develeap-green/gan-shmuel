from app import app

from flask import Flask, abort, request, jsonify
from flask_mysqldb import MySQL

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




if __name__ == '__main__':
    app.run(debug=True)


# @app.route('/')
# def example():
#     return 200
