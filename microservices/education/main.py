import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

import api.models

def create_app():
    app = Flask(__name__)
    secret_key = os.getenv('FLASK_SECRET_KEY')
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = \
                'postgresql+psycopg2://likit@localhost/education_dev'

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from api import education_bp
    app.register_blueprint(education_bp, url_prefix='/api')

    return app