from flask import Flask


def create_app():
    app = Flask(__name__)
    '''
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql+psycopg2://likit@localhost/healthdw_dev'
    '''

    from api import healthservice_blueprint
    app.register_blueprint(healthservice_blueprint, url_prefix='/api')

    return app
