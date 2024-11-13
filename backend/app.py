from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS

from models import db,Client,Worker,ClothingMeasurement,CoatMeasurement,RegularShirtMeasurement,SenatorShirtMeasurement,TrouserMeasurement,Inventory

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = 'UPLOAD_FOLDER'

CORS(app)

migrate = Migrate(app, db)
db.init_app(app)

ma = Marshmallow(app)