import pymysql
from app import db

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
    except Exception as e:
        return {"status": "Failure", "reason": str(e)}

# Utility function for the tables route - testing only
def get_table_contents(table):
    records = db.session.query(table).all()
    return [str(record) for record in records]
