import requests
import pymysql


def check_app_health():
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            return {"status": "OK"}
        else:
            return {"status": "Failure", "reason": "App container is not responding properly"}
    except requests.RequestException as e:
        return {"status": "Failure", "reason": f"Error accessing app container: {str(e)}"}


def check_db_health():
    try:
        connection = pymysql.connect(
            host='db',
            user='user',
            password='pass',
            database='billing',
            port=3306,
            connect_timeout=5
        )
        connection.close()
        return {"status": "OK"}
    except Exception as e:
        return {"status": "Failure", "reason": str(e)}