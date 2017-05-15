from flask import Blueprint

healthservice_blueprint = Blueprint('healthservice', __name__)

from views import *