from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource

db = SQLAlchemy()
ma = Marshmallow()

import api.models

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://likit@localhost/employees'

    ma.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from api import employee_bp
    app.register_blueprint(employee_bp, url_prefix='/api')

    return app