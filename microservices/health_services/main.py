from flask import Flask
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine

mongo = PyMongo()
me = MongoEngine()

def create_app():
    app = Flask(__name__)
    '''
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql+psycopg2://likit@localhost/healthdw_dev'
    '''
    app.config['MONGO_DBNAME'] = 'health_services'
    app.config['MONGODB_DB'] = 'health_services'

    me.init_app(app)
    mongo.init_app(app)

    from api import healthservice_blueprint
    app.register_blueprint(healthservice_blueprint, url_prefix='/api')

    return app
