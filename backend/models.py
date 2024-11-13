from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timezone

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


db = SQLAlchemy(metadata=metadata)

Base = declarative_base()

# Helper function for email validation
def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    clothing_measurements = relationship('ClothingMeasurement', backref='client', lazy=True)

    def __init__(self, username, email, phone=None):
        if not is_valid_email(email):
            raise ValueError("Invalid email format.")
        self.username = username
        self.email = email
        self.phone = phone


class Worker(db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    national_id = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    passport = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relation to inventory and clothing measurements
    clothing_measurements = relationship('ClothingMeasurement', backref='worker', lazy=True)
    inventory_updates = relationship('Inventory', backref='updater', lazy=True)
    
    def __init__(self, username, national_id, email, password, passport=None):
        if not is_valid_email(email):
            raise ValueError("Invalid email format.")
        self.username = username
        self.national_id = national_id
        self.email = email
        self.passport = passport
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class ClothingMeasurement(db.Model):
    __tablename__ = 'clothing_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('clients.id'), nullable=False)
    worker_id = db.Column(db.Integer, ForeignKey('workers.id'), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    coat_measurement = relationship('CoatMeasurement', uselist=False, backref='clothing_measurement', lazy=True)
    regular_shirt_measurement = relationship('RegularShirtMeasurement', uselist=False, backref='clothing_measurement', lazy=True)
    senator_shirt_measurement = relationship('SenatorShirtMeasurement', uselist=False, backref='clothing_measurement', lazy=True)
    trouser_measurement = relationship('TrouserMeasurement', uselist=False, backref='clothing_measurement', lazy=True)


class CoatMeasurement(db.Model):
    __tablename__ = 'coat_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    clothing_measurement_id = db.Column(db.Integer, ForeignKey('clothing_measurements.id'))
    shoulder = db.Column(db.Numeric(5, 2))
    sleeves = db.Column(db.Numeric(5, 2))
    chest = db.Column(db.Numeric(5, 2))
    waist = db.Column(db.Numeric(5, 2))
    arm = db.Column(db.Numeric(5, 2))
    full_length = db.Column(db.Numeric(5, 2))
    bottom_length = db.Column(db.Numeric(5, 2))


class RegularShirtMeasurement(db.Model):
    __tablename__ = 'regular_shirt_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    clothing_measurement_id = db.Column(db.Integer, ForeignKey('clothing_measurements.id'))
    shoulder = db.Column(db.Numeric(5, 2))
    sleeves = db.Column(db.Numeric(5, 2))
    chest = db.Column(db.Numeric(5, 2))
    waist = db.Column(db.Numeric(5, 2))
    arm = db.Column(db.Numeric(5, 2))
    full_length = db.Column(db.Numeric(5, 2))
    bottom_length = db.Column(db.Numeric(5, 2))


class SenatorShirtMeasurement(db.Model):
    __tablename__ = 'senator_shirt_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    clothing_measurement_id = db.Column(db.Integer, ForeignKey('clothing_measurements.id'))
    shoulder = db.Column(db.Numeric(5, 2))
    sleeves = db.Column(db.Numeric(5, 2))
    chest = db.Column(db.Numeric(5, 2))
    waist = db.Column(db.Numeric(5, 2))
    arm = db.Column(db.Numeric(5, 2))
    full_length = db.Column(db.Numeric(5, 2))
    bottom_length = db.Column(db.Numeric(5, 2))
    neck = db.Column(db.Numeric(5, 2))
    wrist = db.Column(db.Numeric(5, 2))


class TrouserMeasurement(db.Model):
    __tablename__ = 'trouser_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    clothing_measurement_id = db.Column(db.Integer, ForeignKey('clothing_measurements.id'))
    waist = db.Column(db.Numeric(5, 2))
    thigh = db.Column(db.Numeric(5, 2))
    knee = db.Column(db.Numeric(5, 2))
    bottom = db.Column(db.Numeric(5, 2))
    fly = db.Column(db.Numeric(5, 2))
    hips = db.Column(db.Numeric(5, 2))


class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updater_id = db.Column(db.Integer, ForeignKey('workers.id'), nullable=False)

    updater = relationship('Worker', backref='inventory_items', lazy=True)


# If needed, to create the tables in the database
if __name__ == '__main__':
    db.create_all()

