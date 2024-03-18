import pymysql
import logging
from app import db
from app.models import Provider, Rates, Trucks

# Configure logger
# logger = logging.getLogger(__name__)

# Utility function for the health-check route.
def check_db_health():
    try:
        with pymysql.connect(
            host='db',
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
        logger.error(f"Database health check failed: {e}")
        return {"status": "Failure", "reason": str(e)}


# Utility function for the tables route - testing only
def get_table_contents(table):
    try:
        records = db.session.query(table).all()
        return [str(record) for record in records]
    except Exception as e:
        logger.error(f"Error retrieving table contents: {e}")
        return []
    

def get_rates():
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
    rates = get_rates()
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
    
