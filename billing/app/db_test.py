from app import app, db
from app.models import Provider, Rates, Trucks
from sqlalchemy import MetaData
import random
import string


#  Function to test the connection to the DB container, after docker compose up.
#  Currently using MYSQL_HOST = '127.0.0.1' in __init__.py, change it to the other option later.
def print_database_tables_and_contents():
    with app.app_context():
        meta = MetaData()
        meta.reflect(bind=db.engine)
        for table in meta.tables.values():
            print(f"Table: {table.name}")
            print_table_contents(table)

        # Add data to each table
        add_data_to_provider()
        add_data_to_rates()
        add_data_to_trucks()

        # Print tables again to see the new data
        for table in meta.tables.values():
            print(f"Table: {table.name}")
            print_table_contents(table)
            print(5 * "-")

def print_table_contents(table):
    records = db.session.query(table).all()
    for record in records:
        print(record)

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def add_data_to_provider():
    new_provider = Provider(name=random_string())
    db.session.add(new_provider)
    db.session.commit()

def add_data_to_rates():
    new_rate = Rates(product_id=random_string(5), rate=random.randint(1, 100), scope=random_string(5))
    db.session.add(new_rate)
    db.session.commit()

def add_data_to_trucks():
    new_truck = Trucks(id=random_string(5), provider_id=random.randint(1, 100))
    db.session.add(new_truck)
    db.session.commit()


if __name__ == '__main__':
    print_database_tables_and_contents()