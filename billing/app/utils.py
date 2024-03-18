import pymysql
import logging
from app import db

# Configure logger
# logger = logging.getLogger(__name__)

# Utility function for the health-check route.
def check_db_health():
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
