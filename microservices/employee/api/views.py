from flask import jsonify
from . import employee_bp as employee
from models import Employee

@employee.route('/employees/')
def get_employees():
    return jsonify({"employees": []})