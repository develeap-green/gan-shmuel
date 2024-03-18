import os
import pandas as pd
from app import db
from app.models import Rates

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