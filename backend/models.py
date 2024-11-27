from app import db
from datetime import datetime, timezone

# Staff Model
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    national_id = db.Column(db.Integer, unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    passport = db.Column(db.String(250), default='logo')
    role = db.Column(db.String(20), nullable=False)  # ADMIN, CEO, MANAGER, TAILOR, STAFF
    # status = db.Column(db.String(20), default='in_consideration')  # Approved, Rejected   >>this is loan status
    salary = db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(250), nullable=False)  # Will store hashed password
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# AdvanceLoan Model
class AdvanceLoan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # ADVANCE or LOAN
    taken_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    status = db.Column(db.String(20), default='in consideration')  # Approved, Rejected, Paid
    comment = db.Column(db.Text, nullable=True)
    date_taken = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# Client Model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(250), nullable=False)  # Will store hashed password
    buying_price = db.Column(db.Integer, nullable=True)
    balance_amount = db.Column(db.Integer, nullable=True)
    pickup_date = db.Column(db.DateTime, nullable=True)
    group_name = db.Column(db.String(20), nullable=True, default='none')
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# CoatMeasurement Model
class CoatMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fabric = db.Column(db.String(50), nullable=False)
    shoulder = db.Column(db.Numeric(5, 2), nullable=True)
    sleeves = db.Column(db.Numeric(5, 2), nullable=True)
    chest = db.Column(db.Numeric(5, 2), nullable=True)
    waist = db.Column(db.Numeric(5, 2), nullable=True)
    arm = db.Column(db.Numeric(5, 2), nullable=True)
    full_length = db.Column(db.Numeric(5, 2), nullable=True)
    bottom_length = db.Column(db.Numeric(5, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='booked')  # On progress, final touches, done, archived
    client = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# RegularShirtMeasurement Model
class RegularShirtMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fabric = db.Column(db.String(50), nullable=False)
    shoulder = db.Column(db.Numeric(5, 2), nullable=True)
    sleeves = db.Column(db.Numeric(5, 2), nullable=True)
    chest = db.Column(db.Numeric(5, 2), nullable=True)
    waist = db.Column(db.Numeric(5, 2), nullable=True)
    arm = db.Column(db.Numeric(5, 2), nullable=True)
    full_length = db.Column(db.Numeric(5, 2), nullable=True)
    bottom_length = db.Column(db.Numeric(5, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='booked')  # On progress, final touches, done, archived
    client = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# SenatorShirtMeasurement Model
class SenatorShirtMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fabric = db.Column(db.String(50), nullable=False)
    shoulder = db.Column(db.Numeric(5, 2), nullable=True)
    sleeves = db.Column(db.Numeric(5, 2), nullable=True)
    chest = db.Column(db.Numeric(5, 2), nullable=True)
    waist = db.Column(db.Numeric(5, 2), nullable=True)
    arm = db.Column(db.Numeric(5, 2), nullable=True)
    full_length = db.Column(db.Numeric(5, 2), nullable=True)
    bottom_length = db.Column(db.Numeric(5, 2), nullable=True)
    neck = db.Column(db.Numeric(5, 2), nullable=True)
    wrist = db.Column(db.Numeric(5, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='booked')  # On progress, final touches, done, archived
    client = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# TrouserMeasurement Model
class TrouserMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fabric = db.Column(db.String(50), nullable=False)
    waist = db.Column(db.Numeric(5, 2), nullable=True)
    thigh = db.Column(db.Numeric(5, 2), nullable=True)
    knee = db.Column(db.Numeric(5, 2), nullable=True)
    bottom = db.Column(db.Numeric(5, 2), nullable=True)
    fly = db.Column(db.Numeric(5, 2), nullable=True)
    hips = db.Column(db.Numeric(5, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='booked')  # On progress, final touches, done, archived
    client = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# Inventory Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Numeric(5, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
