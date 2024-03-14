
from app import db

class ContainersRegistered(db.Model):
    __tablename__ = 'containers_registered'
    
    container_id = db.Column(db.String(15), primary_key=True)
    weight = db.Column(db.Integer)
    unit = db.Column(db.String(10))

    def __repr__(self):
        return f'<Container {self.container_id}>'

class Transactions(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime)
    direction = db.Column(db.String(10))
    truck = db.Column(db.String(50))
    containers = db.Column(db.String(10000))  
    bruto = db.Column(db.Integer)
    truckTara = db.Column(db.Integer)
    neto = db.Column(db.Integer) #"neto": <int> or "na" // na if some of containers unknown
    produce = db.Column(db.String(50))

    def __repr__(self):
        return f'<Transaction {self.id}>'