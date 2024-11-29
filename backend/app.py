from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api, Resource
from models import Staff, AdvanceLoan, Client, CoatMeasurement, RegularShirtMeasurement, SenatorShirtMeasurement, TrouserMeasurement, Inventory
from datetime import datetime,timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chamanenyun'  #secure key

# Initialize the database and Flask-RESTful API
db = SQLAlchemy(app)
api = Api(app)
bcrypt = Bcrypt(app)
session(app)

# Hash the password
def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

# Check if the password matches
def check_password(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if email belongs to staff or client
        user = Staff.query.filter_by(email=email).first()
        if not user:
            user = Client.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        # Store user details in session
        session['user_id'] = user.id
        session['username'] = user.username
        
        # Set role from Staff only, or leave empty if it's a Client
        if isinstance(user, Staff):
            session['role'] = user.role
        else:
            session['role'] = None  # Empty role for clients

        return jsonify({"message": "Login successful", "role": session['role']}), 200

api.add_resource(Login, '/login')

# class SignUp(Resource):
#     def post(self):
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')
#         phone = data.get('phone')
#         email = data.get('email')

#         # Check if email already exists    
#         if Client.query.filter_by(email=email).first():
#             return jsonify({"message": "Email already taken. Kindly Sign in."}), 400

#         # Hash password before saving
#         password_hash = hash_password(password)

#         # Create new client
#         new_user = Client(username=username, password=password_hash, phone=phone, email=email, created_by=1)  # Assuming created_by is the Staff ID (admin or CEO)
#         db.session.add(new_user)
#         db.session.commit()
#         return jsonify({"message": "Client created successfully"}), 201

# api.add_resource(SignUp, '/signup')  # Sign up route for clients only

class Logout(Resource):
    def post(self):
        session.clear()
        return jsonify({"message": "Logged out successfully"}), 200

api.add_resource(Logout, '/logout')

class CreateStaff(Resource):
    def post(self):
        # Check if the logged-in user is Admin or CEO
        if 'role' not in session or session['role'] not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized access"}), 403

        # Get data from request
        data = request.get_json()
        username = data.get('username')
        national_id = data.get('national_id')
        phone = data.get('phone')
        email = data.get('email')
        role = data.get('role')
        salary = data.get('salary')
        password = data.get('password')

        # Check if the email or national ID already exists
        if Staff.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400
        if Staff.query.filter_by(national_id=national_id).first():
            return jsonify({"message": "National ID already exists"}), 400

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Create the staff record
        staff = Staff(username=username, national_id=national_id, phone=phone,
                      email=email, role=role, salary=salary, password=hashed_password)

        # Add to the database
        db.session.add(staff)
        db.session.commit()

        return jsonify({"message": "Staff created successfully"}), 201

api.add_resource(CreateStaff, '/create_staff')

class CreateClient(Resource):
    def post(self):
        # Check if the logged-in user is Admin or CEO
        if 'role' not in session and session['role'] not in ['ADMIN', 'CEO', "MANAGER"]:
            return jsonify({"message": "Unauthorized access"}), 403

        # Get data from request
        data = request.get_json()
        username = data.get('username')
        phone = data.get('phone')
        email = data.get('email')
        buying_price = data.get('buying_price')
        balance_amount = data.get('balance_amount')
        pickup_date = data.get('pickup_date')
        group_name = data.get('group_name')
        created_by = data.get('created_by')  # This should be the ID of the admin/ceo/manager who is currently on session
        password = data.get('password')

        # Check if the email already exists
        if Client.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        # Check if created_by exists and is an Admin or CEO
        creator = Staff.query.get(created_by)
        if not creator or creator.role not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized creator"}), 403

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Create the client record
        client = Client(username=username, phone=phone, email=email, 
                        buying_price=buying_price, balance_amount=balance_amount,
                        pickup_date=pickup_date, group_name=group_name,
                        created_by=created_by, password=hashed_password)

        # Add to the database
        db.session.add(client)
        db.session.commit()

        return jsonify({"message": "Client created successfully"}), 201

api.add_resource(CreateClient, '/create_client')

# Home route
class Home(Resource):
    def get(self):
        if 'user_id' in session:
            return f"Welcome back, {session['user_name']}!"
        return "Welcome to the Inventory Management System!"

api.add_resource(Home, '/')

# Staff routes
class StaffList(Resource):
    def get(self):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401
        
        staff = Staff.query.all()
        staff_list = []
        for s in staff:
            staff_data = {
                'id': s.id,
                'username': s.username,
                'phone': s.phone,
                'email': s.email,
                'passport': s.passport,
                'role': s.role,
                'status': s.status
            }
            staff_list.append(staff_data)
        
        return jsonify(staff_list)

api.add_resource(StaffList, '/staffs')


class StaffResource(Resource):
    def get(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        staff = Staff.query.get(id)
        if not staff:
            return jsonify({"message": "Staff not found"}), 404
        
        staff_data = {
            'id': staff.id,
            'username': staff.username,
            'national_id': staff.national_id,
            'phone': staff.phone,
            'email': staff.email,
            'passport': staff.passport,
            'role': staff.role,
            'status': staff.status,
            'salary': staff.salary,
            'created_at': staff.created_at
        }
        
        return jsonify(staff_data)

    def patch(self, id):
        if 'user_id' not in session or session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        staff = Staff.query.get(id)
        if not staff:
            return jsonify({"message": "Staff not found"}), 404
        
        data = request.get_json()
        if 'username' in data:
            staff.username = data['username']
        if 'phone' in data:
            staff.phone = data['phone']
        if 'email' in data:
            staff.email = data['email']
        if 'role' in data:
            staff.role = data['role']
        if 'salary' in data:
            staff.salary = data['salary']
        if 'status' in data:
            staff.status = data['status']
        
        db.session.commit()
        
        return jsonify({"message": "Staff updated successfully"})

    def delete(self, id):
        if 'user_id' not in session or session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        staff = Staff.query.get(id)
        if not staff:
            return jsonify({"message": "Staff not found"}), 404
        
        db.session.delete(staff)
        db.session.commit()
        
        return jsonify({"message": "Staff deleted successfully"})

api.add_resource(StaffResource, '/staff/<int:id>')


# Client routes
class ClientList(Resource):
    def get(self):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        clients = Client.query.all()
        clients_list = []
        for c in clients:
            client_data = {
                'id': c.id,
                'username': c.username,
                'phone': c.phone,
                'email': c.email,
                'balance_amount': c.balance_amount,
                'pickup_date': c.pickup_date,
                'group_name': c.group_name,
                'created_by': c.created_by,
                'date_created': c.date_created
            }
            clients_list.append(client_data)
        
        return jsonify(clients_list)

    def post(self):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO']:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json()
        username = data['username']
        phone = data['phone']
        email = data['email']
        password = generate_password_hash(data['password'], method='sha256')  # Hashing password
        balance_amount = data['balance_amount']
        pickup_date = data['pickup_date']
        
        new_client = Client(
            username=username,
            phone=phone,
            email=email,
            password=password,
            balance_amount=balance_amount,
            pickup_date=pickup_date,
            created_by=session['user_id'],  # Set the client as created by the staff in session
            date_created=datetime.now()
        )
        
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({"message": "Client added successfully"}), 201

api.add_resource(ClientList, '/clients')


class ClientResource(Resource):
    def get(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        client = Client.query.get(id)
        if not client:
            return jsonify({"message": "Client not found"}), 404
        
        client_data = {
            'id': client.id,
            'username': client.username,
            'phone': client.phone,
            'email': client.email,
            'balance_amount': client.balance_amount,
            'pickup_date': client.pickup_date,
            'group_name': client.group_name,
            'created_by': client.created_by,
            'date_created': client.date_created
        }
        
        return jsonify(client_data)

    def patch(self, id):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        client = Client.query.get(id)
        if not client:
            return jsonify({"message": "Client not found"}), 404
        
        data = request.get_json()
        if 'username' in data:
            client.username = data['username']
        if 'phone' in data:
            client.phone = data['phone']
        if 'email' in data:
            client.email = data['email']
        if 'balance_amount' in data:
            client.balance_amount = data['balance_amount']
        if 'pickup_date' in data:
            client.pickup_date = data['pickup_date']
        
        db.session.commit()
        
        return jsonify({"message": "Client updated successfully"})

    def delete(self, id):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        client = Client.query.get(id)
        if not client:
            return jsonify({"message": "Client not found"}), 404
        
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({"message": "Client deleted successfully"})

api.add_resource(ClientResource, '/client/<int:id>')

    
# Advance Loan routes
class AdvanceLoanList(Resource):
    def get(self):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        loans = AdvanceLoan.query.all()
        loan_list = []
        for loan in loans:
            loan_data = {
                'id': loan.id,
                'client_id': loan.client_id,
                'loan_amount': loan.loan_amount,
                'status': loan.status,
                'date_approved': loan.date_approved,
                'approved_by': loan.approved_by,
                'date_created': loan.date_created
            }
            loan_list.append(loan_data)
        
        return jsonify(loan_list)

    # def post(self):
    #     if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', "MANAGER", "STAFF", "TAILOR"]:
    #         return jsonify({"message": "Unauthorized"}), 401

    #     data = request.get_json()
    #     client_id = data['client_id']
    #     loan_amount = data['loan_amount']
    #     status = data['status']
    #     approved_by = session['user_id']

    #     new_loan = AdvanceLoan(
    #         client_id=client_id,
    #         loan_amount=loan_amount,
    #         status=status,
    #         approved_by=approved_by,
    #         date_approved=datetime.now(),
    #         date_created=datetime.now()
    #     )

    #     db.session.add(new_loan)
    #     db.session.commit()

    #     return jsonify({"message": "Loan added successfully"}), 201

api.add_resource(AdvanceLoanList, '/advance_loans')

class AdvanceLoanResource(Resource):
    def get(self, id):
        # Check if the user is authorized
        if 'user_id' not in session :
            return jsonify({"message": "Unauthorized"}), 401

        # Query for all loans taken by the staff member with the given ID
        loans = AdvanceLoan.query.filter_by(taken_by=id).all()  # Replace 'staff_id' with the actual field name

        # Check if any loans were found
        if not loans:
            return jsonify({"message": "No loans found for this staff member"}), 404

        # Prepare the list of loan data
        loans_data = []
        for loan in loans:
            loans_data.append({
                'id': loan.id,
                'client_id': loan.client_id,
                'loan_amount': loan.loan_amount,
                'status': loan.status,
                'date_approved': loan.date_approved,
                'approved_by': loan.approved_by,
                'date_created': loan.date_created
            })

        # Return the list of loans
        return jsonify(loans_data)


    def patch(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        loan = AdvanceLoan.query.get(id)
        if not loan:
            return jsonify({"message": "Loan not found"}), 404
        
        # Ensure the loan was taken less than 10 minutes ago
        current_time = datetime.now(timezone.utc)
        time_difference = current_time - loan.date_taken
        if time_difference > timedelta(minutes=10):
            return jsonify({"message": "Loan can no longer be updated"}), 403
        
        data = request.get_json()
        if 'loan_amount' in data:
            loan.loan_amount = data['loan_amount']
        if 'status' in data:
            loan.status = data['status']

        db.session.commit()

        return jsonify({"message": "Loan updated successfully"})

    def delete(self, id):
        if 'user_id' not in session or session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        loan = AdvanceLoan.query.get(id)
        if not loan:
            return jsonify({"message": "Loan not found"}), 404
        
        db.session.delete(loan)
        db.session.commit()

        return jsonify({"message": "Loan deleted successfully"})

api.add_resource(AdvanceLoanResource, '/advance_loan/<int:id>')


class CoatMeasurementList(Resource):
    def get(self):
        # Ensure the user is authenticated
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch all coat measurements
        measurements = CoatMeasurement.query.all()
        measurement_list = []
        for m in measurements:
            # Match fields from the model
            measurement_data = {
                'id': m.id,
                'fabric': m.fabric,
                'shoulder': float(m.shoulder) if m.shoulder else None,
                'sleeves': float(m.sleeves) if m.sleeves else None,
                'chest': float(m.chest) if m.chest else None,
                'waist': float(m.waist) if m.waist else None,
                'arm': float(m.arm) if m.arm else None,
                'full_length': float(m.full_length) if m.full_length else None,
                'bottom_length': float(m.bottom_length) if m.bottom_length else None,
                'description': m.description,
                'status': m.status,
                'client': m.client,
                'assigned_to': m.assigned_to,
                'created_by': m.created_by,
                'date_created': m.date_created
            }
            measurement_list.append(measurement_data)

        return jsonify(measurement_list)

    # def post(self):
    #     # Ensure the user is authenticated
    #     if 'user_id' not in session:
    #         return jsonify({"message": "Unauthorized"}), 401

    #     # Parse and validate input data
    #     data = request.get_json()
    #     required_fields = ['fabric', 'client']
    #     for field in required_fields:
    #         if field not in data:
    #             return jsonify({"message": f"'{field}' is required"}), 400

    #     # Extract and assign data to the new measurement
    #     new_measurement = CoatMeasurement(
    #         fabric=data['fabric'],
    #         shoulder=data.get('shoulder'),
    #         sleeves=data.get('sleeves'),
    #         chest=data.get('chest'),
    #         waist=data.get('waist'),
    #         arm=data.get('arm'),
    #         full_length=data.get('full_length'),
    #         bottom_length=data.get('bottom_length'),
    #         description=data.get('description'),
    #         status=data.get('status', 'booked'),  # Default status if not provided
    #         client=data['client'],
    #         assigned_to=data.get('assigned_to'),
    #         created_by=session['user_id'],  # Assuming the session contains the creator's ID
    #         date_created=datetime.now(timezone.utc)
    #     )

    #     # Save to the database
    #     db.session.add(new_measurement)
    #     db.session.commit()

    #     return jsonify({"message": "Coat measurement added successfully", "id": new_measurement.id}), 201


# Add the resource to the API
api.add_resource(CoatMeasurementList, '/coat_measurements')


class CoatMeasurementResource(Resource):
    def get(self, id):
        # Ensure the user is authenticated
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch the coat measurement by ID
        measurement = CoatMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404
        
        # Construct the response data
        measurement_data = {
            'id': measurement.id,
            'fabric': measurement.fabric,
            'shoulder': float(measurement.shoulder) if measurement.shoulder else None,
            'sleeves': float(measurement.sleeves) if measurement.sleeves else None,
            'chest': float(measurement.chest) if measurement.chest else None,
            'waist': float(measurement.waist) if measurement.waist else None,
            'arm': float(measurement.arm) if measurement.arm else None,
            'full_length': float(measurement.full_length) if measurement.full_length else None,
            'bottom_length': float(measurement.bottom_length) if measurement.bottom_length else None,
            'description': measurement.description,
            'status': measurement.status,
            'client': measurement.client,
            'assigned_to': measurement.assigned_to,
            'created_by': measurement.created_by,
            'date_created': measurement.date_created
        }

        return jsonify(measurement_data)

    def patch(self, id):
        # Ensure the user is authenticated
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch the coat measurement by ID
        measurement = CoatMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404
        
        # Get the request data
        data = request.get_json()

        # Update fields if they are provided in the request
        if 'fabric' in data:
            measurement.fabric = data['fabric']
        if 'shoulder' in data:
            measurement.shoulder = data['shoulder']
        if 'sleeves' in data:
            measurement.sleeves = data['sleeves']
        if 'chest' in data:
            measurement.chest = data['chest']
        if 'waist' in data:
            measurement.waist = data['waist']
        if 'arm' in data:
            measurement.arm = data['arm']
        if 'full_length' in data:
            measurement.full_length = data['full_length']
        if 'bottom_length' in data:
            measurement.bottom_length = data['bottom_length']
        if 'description' in data:
            measurement.description = data['description']
        if 'status' in data:
            measurement.status = data['status']
        if 'assigned_to' in data:
            measurement.assigned_to = data['assigned_to']

        # Commit the changes
        db.session.commit()

        return jsonify({"message": "Coat measurement updated successfully"})

    def delete(self, id):
        # Ensure the user is authenticated and authorized
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch the coat measurement by ID
        measurement = CoatMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404
        
        # Delete the record
        db.session.delete(measurement)
        db.session.commit()

        return jsonify({"message": "Coat measurement deleted successfully"})

# Add the resource to the API
api.add_resource(CoatMeasurementResource, '/coat_measurement/<int:id>')

class RegularShirtMeasurementList(Resource):
    def get(self):
        # Ensure the user is authenticated
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch all regular shirt measurements
        measurements = RegularShirtMeasurement.query.all()
        measurement_list = []
        for m in measurements:
            # Match fields from the model
            measurement_data = {
                'id': m.id,
                'fabric': m.fabric,
                'shoulder': float(m.shoulder) if m.shoulder else None,
                'sleeves': float(m.sleeves) if m.sleeves else None,
                'chest': float(m.chest) if m.chest else None,
                'waist': float(m.waist) if m.waist else None,
                'arm': float(m.arm) if m.arm else None,
                'full_length': float(m.full_length) if m.full_length else None,
                'bottom_length': float(m.bottom_length) if m.bottom_length else None,
                'description': m.description,
                'status': m.status,
                'client': m.client,
                'assigned_to': m.assigned_to,
                'created_by': m.created_by,
                'date_created': m.date_created
            }
            measurement_list.append(measurement_data)

        return jsonify(measurement_list)

    # def post(self):
    #     # Ensure the user is authenticated
    #     if 'user_id' not in session:
    #         return jsonify({"message": "Unauthorized"}), 401

    #     # Parse and validate input data
    #     data = request.get_json()
    #     required_fields = ['fabric', 'client']
    #     for field in required_fields:
    #         if field not in data:
    #             return jsonify({"message": f"'{field}' is required"}), 400

    #     # Extract and assign data to the new measurement
    #     new_measurement = RegularShirtMeasurement(
    #         fabric=data['fabric'],
    #         shoulder=data.get('shoulder'),
    #         sleeves=data.get('sleeves'),
    #         chest=data.get('chest'),
    #         waist=data.get('waist'),
    #         arm=data.get('arm'),
    #         full_length=data.get('full_length'),
    #         bottom_length=data.get('bottom_length'),
    #         description=data.get('description'),
    #         status=data.get('status', 'booked'),  # Default status if not provided
    #         client=data['client'],
    #         assigned_to=data.get('assigned_to'),
    #         created_by=session['user_id'],  # Assuming the session contains the creator's ID
    #         date_created=datetime.now(timezone.utc)
    #     )

    #     # Save to the database
    #     db.session.add(new_measurement)
    #     db.session.commit()

    #     return jsonify({"message": "Regular shirt measurement added successfully", "id": new_measurement.id}), 201


# Add the resource to the API
api.add_resource(RegularShirtMeasurementList, '/regular_shirt_measurements')

class RegularShirtMeasurementResource(Resource):
    def get(self, id):
        # Ensure the user is authenticated
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch the specific measurement by ID
        measurement = RegularShirtMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404

        # Serialize measurement data
        measurement_data = {
            'id': measurement.id,
            'fabric': measurement.fabric,
            'shoulder': float(measurement.shoulder) if measurement.shoulder else None,
            'sleeves': float(measurement.sleeves) if measurement.sleeves else None,
            'chest': float(measurement.chest) if measurement.chest else None,
            'waist': float(measurement.waist) if measurement.waist else None,
            'arm': float(measurement.arm) if measurement.arm else None,
            'full_length': float(measurement.full_length) if measurement.full_length else None,
            'bottom_length': float(measurement.bottom_length) if measurement.bottom_length else None,
            'description': measurement.description,
            'status': measurement.status,
            'client': measurement.client,
            'assigned_to': measurement.assigned_to,
            'created_by': measurement.created_by,
            'date_created': measurement.date_created
        }

        return jsonify(measurement_data)

    def patch(self, id):
        # Ensure the user is authenticated
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch the specific measurement by ID
        measurement = RegularShirtMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404

        # Parse and apply updates
        data = request.get_json()
        if 'fabric' in data:
            measurement.fabric = data['fabric']
        if 'shoulder' in data:
            measurement.shoulder = data['shoulder']
        if 'sleeves' in data:
            measurement.sleeves = data['sleeves']
        if 'chest' in data:
            measurement.chest = data['chest']
        if 'waist' in data:
            measurement.waist = data['waist']
        if 'arm' in data:
            measurement.arm = data['arm']
        if 'full_length' in data:
            measurement.full_length = data['full_length']
        if 'bottom_length' in data:
            measurement.bottom_length = data['bottom_length']
        if 'description' in data:
            measurement.description = data['description']
        if 'status' in data:
            measurement.status = data['status']
        if 'assigned_to' in data:
            measurement.assigned_to = data['assigned_to']

        db.session.commit()

        return jsonify({"message": "Regular shirt measurement updated successfully"})

    def delete(self, id):
        # Ensure the user is authenticated and authorized
        if 'user_id' not in session or session.get('role') not in ['ADMIN', 'CEO']:
            return jsonify({"message": "Unauthorized"}), 401

        # Fetch the specific measurement by ID
        measurement = RegularShirtMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404

        # Delete the measurement
        db.session.delete(measurement)
        db.session.commit()

        return jsonify({"message": "Regular shirt measurement deleted successfully"})


# Add the resource to the API
api.add_resource(RegularShirtMeasurementResource, '/regular_shirt_measurement/<int:id>')

class SenatorShirtMeasurementList(Resource):
    def get(self):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        measurements = SenatorShirtMeasurement.query.all()
        measurement_list = []
        for m in measurements:
            measurement_data = {
                'id': m.id,
                'fabric': m.fabric,
                'shoulder': float(m.shoulder) if m.shoulder else None,
                'sleeves': float(m.sleeves) if m.sleeves else None,
                'chest': float(m.chest) if m.chest else None,
                'waist': float(m.waist) if m.waist else None,
                'arm': float(m.arm) if m.arm else None,
                'full_length': float(m.full_length) if m.full_length else None,
                'bottom_length': float(m.bottom_length) if m.bottom_length else None,
                'neck': float(m.neck) if m.neck else None,
                'wrist': float(m.wrist) if m.wrist else None,
                'description': m.description,
                'status': m.status,
                'client': m.client,
                'assigned_to': m.assigned_to,
                'created_by': m.created_by,
                'date_created': m.date_created
            }
            measurement_list.append(measurement_data)

        return jsonify(measurement_list)
    
    def post(self):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json()

        # Validate required fields
        if 'fabric' not in data or 'client' not in data or 'created_by' not in data:
            return jsonify({"message": "Missing required fields: fabric, client, and created_by"}), 400

        new_measurement = SenatorShirtMeasurement(
            fabric=data['fabric'],
            shoulder=data.get('shoulder'),
            sleeves=data.get('sleeves'),
            chest=data.get('chest'),
            waist=data.get('waist'),
            arm=data.get('arm'),
            full_length=data.get('full_length'),
            bottom_length=data.get('bottom_length'),
            neck=data.get('neck'),
            wrist=data.get('wrist'),
            description=data.get('description'),
            status=data.get('status', 'booked'),
            client=data['client'],
            assigned_to=data.get('assigned_to'),
            created_by=data['created_by'],
            date_created=datetime.now(timezone.utc)
        )

        db.session.add(new_measurement)
        db.session.commit()

        return jsonify({"message": "Senator shirt measurement added successfully"}), 201


api.add_resource(SenatorShirtMeasurementList, '/senator_shirt_measurements')

class SenatorShirtMeasurementResource(Resource):
    def get(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        measurement = SenatorShirtMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404
        
        measurement_data = {
            'id': measurement.id,
            'client_id': measurement.client_id,
            'chest': measurement.chest,
            'waist': measurement.waist,
            'hips': measurement.hips,
            'sleeve_length': measurement.sleeve_length,
            'collar': measurement.collar,
            'neck': measurement.neck,
            'date_created': measurement.date_created
        }

        return jsonify(measurement_data)

    def patch(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        measurement = SenatorShirtMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404
        
        data = request.get_json()
        if 'chest' in data:
            measurement.chest = data['chest']
        if 'waist' in data:
            measurement.waist = data['waist']
        if 'hips' in data:
            measurement.hips = data['hips']
        if 'sleeve_length' in data:
            measurement.sleeve_length = data['sleeve_length']
        if 'collar' in data:
            measurement.collar = data['collar']
        if 'neck' in data:
            measurement.neck = data['neck']

        db.session.commit()

        return jsonify({"message": "Senator shirt measurement updated successfully"})

    def delete(self, id):
        if 'user_id' not in session or session.get('role') not in ['ADMIN', 'CEO']:
            return jsonify({"message": "Unauthorized"}), 401

        measurement = SenatorShirtMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404
        
        db.session.delete(measurement)
        db.session.commit()

        return jsonify({"message": "Senator shirt measurement deleted successfully"})

api.add_resource(SenatorShirtMeasurementResource, '/senator_shirt_measurement/<int:id>')

class TrouserMeasurementList(Resource):
    def get(self):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        measurements = TrouserMeasurement.query.all()
        measurement_list = []
        for m in measurements:
            measurement_data = {
                'id': m.id,
                'fabric': m.fabric,
                'waist': float(m.waist) if m.waist else None,
                'thigh': float(m.thigh) if m.thigh else None,
                'knee': float(m.knee) if m.knee else None,
                'bottom': float(m.bottom) if m.bottom else None,
                'fly': float(m.fly) if m.fly else None,
                'hips': float(m.hips) if m.hips else None,
                'description': m.description,
                'status': m.status,
                'client': m.client,
                'assigned_to': m.assigned_to,
                'created_by': m.created_by,
                'date_created': m.date_created
            }
            measurement_list.append(measurement_data)

        return jsonify(measurement_list)
    
    def post(self):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json()

        # Validate required fields
        if 'fabric' not in data or 'client' not in data or 'created_by' not in data:
            return jsonify({"message": "Missing required fields: fabric, client, and created_by"}), 400

        new_measurement = TrouserMeasurement(
            fabric=data['fabric'],
            waist=data.get('waist'),
            thigh=data.get('thigh'),
            knee=data.get('knee'),
            bottom=data.get('bottom'),
            fly=data.get('fly'),
            hips=data.get('hips'),
            description=data.get('description'),
            status=data.get('status', 'booked'),
            client=data['client'],
            assigned_to=data.get('assigned_to'),
            created_by=data['created_by'],
            date_created=datetime.now(timezone.utc)
        )

        db.session.add(new_measurement)
        db.session.commit()

        return jsonify({"message": "Trouser measurement added successfully"}), 201


api.add_resource(TrouserMeasurementList, '/trouser_measurements')


class TrouserMeasurementResource(Resource):
    def get(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        measurement = TrouserMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404

        measurement_data = {
            'id': measurement.id,
            'fabric': measurement.fabric,
            'waist': float(measurement.waist) if measurement.waist else None,
            'thigh': float(measurement.thigh) if measurement.thigh else None,
            'knee': float(measurement.knee) if measurement.knee else None,
            'bottom': float(measurement.bottom) if measurement.bottom else None,
            'fly': float(measurement.fly) if measurement.fly else None,
            'hips': float(measurement.hips) if measurement.hips else None,
            'description': measurement.description,
            'status': measurement.status,
            'client': measurement.client,
            'assigned_to': measurement.assigned_to,
            'created_by': measurement.created_by,
            'date_created': measurement.date_created
        }

        return jsonify(measurement_data)

    def patch(self, id):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        measurement = TrouserMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404

        data = request.get_json()
        if 'fabric' in data:
            measurement.fabric = data['fabric']
        if 'waist' in data:
            measurement.waist = data['waist']
        if 'thigh' in data:
            measurement.thigh = data['thigh']
        if 'knee' in data:
            measurement.knee = data['knee']
        if 'bottom' in data:
            measurement.bottom = data['bottom']
        if 'fly' in data:
            measurement.fly = data['fly']
        if 'hips' in data:
            measurement.hips = data['hips']
        if 'description' in data:
            measurement.description = data['description']
        if 'status' in data:
            measurement.status = data['status']
        if 'assigned_to' in data:
            measurement.assigned_to = data['assigned_to']

        db.session.commit()

        return jsonify({"message": "Trouser measurement updated successfully"})

    def delete(self, id):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        measurement = TrouserMeasurement.query.get(id)
        if not measurement:
            return jsonify({"message": "Measurement not found"}), 404

        db.session.delete(measurement)
        db.session.commit()

        return jsonify({"message": "Trouser measurement deleted successfully"})


api.add_resource(TrouserMeasurementResource, '/trouser_measurement/<int:id>')

# Inventory
class InventoryList(Resource):
    def get(self):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        inventories = Inventory.query.all()
        inventory_list = []
        for inventory in inventories:
            inventory_data = {
                'id': inventory.id,
                'item_name': inventory.item_name,
                'quantity': inventory.quantity,
                'description': inventory.description,
                'created_by': inventory.created_by,
                'date_created': inventory.date_created
            }
            inventory_list.append(inventory_data)

        return jsonify(inventory_list)

    def post(self):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json()

        # Validate required fields
        if 'item_name' not in data or 'quantity' not in data or 'created_by' not in data:
            return jsonify({"message": "Missing required fields: item_name, quantity, and created_by"}), 400

        new_inventory = Inventory(
            item_name=data['item_name'],
            quantity=data['quantity'],
            description=data.get('description'),
            created_by=data['created_by'],
            date_created=datetime.now(timezone.utc)
        )

        db.session.add(new_inventory)
        db.session.commit()

        return jsonify({"message": "Inventory item added successfully"}), 201
    
api.add_resource(InventoryList, '/inventories')

class InventoryResource(Resource):
    def get(self, id):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized"}), 401

        inventory = Inventory.query.get(id)
        if not inventory:
            return jsonify({"message": "Inventory item not found"}), 404

        inventory_data = {
            'id': inventory.id,
            'item_name': inventory.item_name,
            'quantity': inventory.quantity,
            'description': inventory.description,
            'created_by': inventory.created_by,
            'date_created': inventory.date_created
        }

        return jsonify(inventory_data)

    def patch(self, id):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        inventory = Inventory.query.get(id)
        if not inventory:
            return jsonify({"message": "Inventory item not found"}), 404

        data = request.get_json()

        if 'item_name' in data:
            inventory.item_name = data['item_name']
        if 'quantity' in data:
            inventory.quantity = data['quantity']
        if 'description' in data:
            inventory.description = data['description']

        db.session.commit()

        return jsonify({"message": "Inventory item updated successfully"})

    def delete(self, id):
        if 'user_id' not in session and session.get('role') not in ['ADMIN', 'CEO', 'MANAGER']:
            return jsonify({"message": "Unauthorized"}), 401

        inventory = Inventory.query.get(id)
        if not inventory:
            return jsonify({"message": "Inventory item not found"}), 404

        db.session.delete(inventory)
        db.session.commit()

        return jsonify({"message": "Inventory item deleted successfully"})

api.add_resource(InventoryResource, '/inventory/<int:id>')

if __name__ == "__main__":
    app.run(debug=True)
