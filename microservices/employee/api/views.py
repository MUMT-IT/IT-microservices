from flask import jsonify
from flask_restful import Api, Resource
from . import employee_bp
from models import Employee, EmployeeSchema
from flask_restful.utils import cors

api = Api(employee_bp)

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

class EmployeeResource(Resource):
    def get(self, id):
        empl = Employee.query.get_or_404(id)
        result = employee_schema.dump(empl).data
        return jsonify({'employee': result})

class EmployeeListResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        empls = Employee.query.all()
        result = employees_schema.dump(empls).data
        return jsonify({'employees': result})

api.add_resource(EmployeeResource, '/employees/<int:id>')
api.add_resource(EmployeeListResource, '/employees/')