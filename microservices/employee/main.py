from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import api.models

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from api import employee_bp
    app.register_blueprint(employee_bp, url_prefix='/api')

    return app