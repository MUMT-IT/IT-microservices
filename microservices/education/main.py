import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine

mongo = PyMongo()
me = MongoEngine()

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    secret_key = os.getenv('FLASK_SECRET_KEY')
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = \
                'postgresql+psycopg2://likit@localhost/education_dev'
    app.config['MONGO_DBNAME'] = 'employees'
    app.config['MONGODB_DB'] = 'employees'

    me.init_app(app)
    mongo.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from api import education_bp
    app.register_blueprint(education_bp, url_prefix='/api')

    return app