from flask_script import Manager
from flask import Flask

def create_app():
    app = Flask(__name__)

    from api import education_bp
    app.register_blueprint(education_bp, url_prefix='/api')

    return app

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
    #app.run()