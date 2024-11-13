#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.security import  generate_password_hash
from flask_cors import CORS
from models import db, Client, Worker, ClothingMeasurement, CoatMeasurement, RegularShirtMeasurement, SenatorShirtMeasurement, TrouserMeasurement, Inventory

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)
ma = Marshmallow(app)

# Marshmallow Schemas
class ClientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        load_instance = True

client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

class WorkerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Worker
        load_instance = True
        exclude = ('password',)

worker_schema = WorkerSchema()
workers_schema = WorkerSchema(many=True)

class ClothingMeasurementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClothingMeasurement
        load_instance = True

clothing_measurement_schema = ClothingMeasurementSchema()
clothing_measurements_schema = ClothingMeasurementSchema(many=True)

class CoatMeasurementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CoatMeasurement
        load_instance = True

coat_measurement_schema = CoatMeasurementSchema()

class RegularShirtMeasurementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RegularShirtMeasurement
        load_instance = True

regular_shirt_measurement_schema = RegularShirtMeasurementSchema()

class SenatorShirtMeasurementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SenatorShirtMeasurement
        load_instance = True

senator_shirt_measurement_schema = SenatorShirtMeasurementSchema()

class TrouserMeasurementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrouserMeasurement
        load_instance = True

trouser_measurement_schema = TrouserMeasurementSchema()

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

# API Resources
api = Api(app)

class Index(Resource):
    def get(self):
        return jsonify({"message": "This is Star Tailored Designs MIS developer by Ronoh Immanuel Cheruiyot!"})

api.add_resource(Index, '/')

class ClientList(Resource):
    def get(self):
        clients = Client.query.all()
        return clients_schema.dump(clients)

    def post(self):
        data = request.get_json()
        client = client_schema.load(data)
        db.session.add(client)
        db.session.commit()
        return client_schema.dump(client), 201

api.add_resource(ClientList, '/clients')

class ClientDetail(Resource):
    def get(self, id):
        client = Client.query.get_or_404(id)
        return client_schema.dump(client)

    def delete(self, id):
        client = Client.query.get_or_404(id)
        db.session.delete(client)
        db.session.commit()
        return {"message": "Client deleted"}, 200

api.add_resource(ClientDetail, '/clients/<int:id>')

class WorkerList(Resource):
    def get(self):
        workers = Worker.query.all()
        return workers_schema.dump(workers)

    def post(self):
        data = request.get_json()
        data['password'] = generate_password_hash(data['password'])
        worker = worker_schema.load(data)
        db.session.add(worker)
        db.session.commit()
        return worker_schema.dump(worker), 201

api.add_resource(WorkerList, '/workers')

class WorkerDetail(Resource):
    def get(self, id):
        worker = Worker.query.get_or_404(id)
        return worker_schema.dump(worker)

    def delete(self, id):
        worker = Worker.query.get_or_404(id)
        db.session.delete(worker)
        db.session.commit()
        return {"message": "Worker deleted"}, 200

api.add_resource(WorkerDetail, '/workers/<int:id>')

class InventoryList(Resource):
    def get(self):
        inventories = Inventory.query.all()
        return inventories_schema.dump(inventories)

    def post(self):
        data = request.get_json()
        inventory = inventory_schema.load(data)
        db.session.add(inventory)
        db.session.commit()
        return inventory_schema.dump(inventory), 201

api.add_resource(InventoryList, '/inventory')

class InventoryDetail(Resource):
    def get(self, id):
        inventory = Inventory.query.get_or_404(id)
        return inventory_schema.dump(inventory)

    def delete(self, id):
        inventory = Inventory.query.get_or_404(id)
        db.session.delete(inventory)
        db.session.commit()
        return {"message": "Inventory item deleted"}, 200

api.add_resource(InventoryDetail, '/inventory/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
