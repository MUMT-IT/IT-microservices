import os
from flask_script import Manager
from flask import Flask

def create_app():
    app = Flask(__name__)
    secret_key = os.getenv('FLASK_SECRET_KEY')
    app.config['SECRET_KEY'] = secret_key

    from api import education_bp
    app.register_blueprint(education_bp, url_prefix='/api')

    return app

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
    #app.run()