from app import db

class Provider(db.Model):
    __tablename__ = 'Provider'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))

    def __repr__(self):
        return f"<Provider(id={self.id}, name={self.name})>"

class Rates(db.Model):
    __tablename__ = 'Rates'
    product_id = db.Column(db.String(50), primary_key=True)
    rate = db.Column(db.Integer, default=0)
    scope = db.Column(db.String(50), db.ForeignKey('Provider.id'))

    def __repr__(self):
        return f"<Rates(product_id={self.product_id}, rate={self.rate}, scope={self.scope})>"

class Trucks(db.Model):
    __tablename__ = 'Trucks'
    id = db.Column(db.String(10), primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.id'))

    def __repr__(self):
        return f"<Trucks(id={self.id}, provider_id={self.provider_id})>"
    


