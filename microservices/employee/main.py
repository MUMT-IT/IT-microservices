from flask import Flask
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from flask_cors import CORS

mongo = PyMongo()
me = MongoEngine()
cors = CORS()

def create_app():
    app = Flask(__name__)
    app.config['MONGO_DBNAME'] = 'employees'
    app.config['MONGODB_DB'] = 'employees'

    me.init_app(app)
    mongo.init_app(app)
    cors.init_app(app)

    from api import employee_bp
    app.register_blueprint(employee_bp, url_prefix='/api')

    return app
