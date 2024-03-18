import os
import csv
from app import app, db
from app.models import Rates
import sqlalchemy
from sqlalchemy import and_
from flask import jsonify
import flask_excel as excel

def updateRatesFromFile():
    # Iterate over files in the 'in' directory
    #this works when your pwd is billing - test this!!!!!!!!!!!!!!!!!!!!!!!!!
    for filename in os.listdir('in'):
        file_path = os.path.join('in', filename)
        dataList = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            # For each row in the file, update the rare
            for row in reader:
                dataList.append(row)
            # Update the database Rates:
            for row in dataList:
                option = "" # Flag
                # Query the database to retrieve the product's objects by Provider id (scope)
                # Retrive all the products by product id
                if row['Scope'] == 'All':
                    option = "All providers"
                    providerProduct = Rates.query.filter_by(product_id=row['Product']).all()
                # Retrive all the producte by product id and provider id (scope)
                elif row['Scope'] != 'All' and row['Scope'] != None:
                    option = "specific provider"
                    providerProduct = Rates.query.filter(and_(Rates.scope == row['Scope'], Rates.product_id == row['Product'])).all()
                # Update the product rate
                if option == "specific provider":
                    for product in providerProduct:
                        providerProduct.rate = row['Rate']
                elif option == "All providers":
                    for product in providerProduct:
                        product.rate = row['Rate']
            # Commit changes to the database
#            providerProduct.commit()
            db.session.commit()
    return "updated"


def getRates():

    querySets = Rates.query.all()
    if not querySets:
        return jsonify({"error": "No data available to download"}), 404

    columns = ['product_id', 'rate', 'scope']

    try:
        return excel.make_response_from_query_sets(
                query_sets=querySets, 
                column_names=columns,
                file_type='csv',
                file_name='rates'
                )
    except Exception as e:
                app.logger.error(f"Error generating csv file: {e}")
                return jsonify({"error": "Error generating csv file"}), 500
