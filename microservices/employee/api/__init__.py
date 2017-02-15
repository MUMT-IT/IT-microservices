from flask import Blueprint

employee_bp = Blueprint('employees', __name__)

from . import views