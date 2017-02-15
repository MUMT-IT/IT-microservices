from flask import Flask

def create_app():
    app = Flask(__name__)

    from api import employee_bp
    app.register_blueprint(employee_bp, url_prefix='/api')

    return app