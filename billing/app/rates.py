import os
import pandas as pd
from app import db
from app.models import Rates
from flask import jsonify
import flask_excel as excel


def updateRatesFromFile():
    in_directory = os.path.abspath('in')
    file_path = os.path.join(in_directory, 'rates.csv')
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the Excel file into a DataFrame
        df = pd.read_csv(file_path)


        # Remove all existing rates from the database
        db.session.query(Rates).delete()
        
        # Add the database all rates from the file
        for _, row in df.iterrows():
            # Add new rate
            rate = Rates(product_id=row['product'], rate=row['rate'], scope=row['scope'])
            db.session.add(rate)
        
        # Commit the changes to the database
        db.session.commit()
        return "Database updated successfully"

    else:
        return "File does not exist"


def getRates():
    # Query and save Rates table from Rates db model (typically rows), return 404 if not found
    querySets = Rates.query.all()
    if not querySets:
        return jsonify({"error": "No data available to download"}), 404
    # Create list of columns based on Rates db model
    columns = ['product_id', 'rate', 'scope']
    # Try to return a csv file named rates based on the saved query sets and columns
    try:
        return excel.make_response_from_query_sets(
                query_sets=querySets,
                column_names=columns,
                file_type='csv',
                file_name='rates'
                )
    # Except: log and return json if file generation failed
    except Exception as e:
                app.logger.error(f"Error generating csv file: {e}")
                return jsonify({"error": "Error generating csv file"}), 500