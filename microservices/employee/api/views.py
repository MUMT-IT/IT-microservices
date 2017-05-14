import json
from flask import request, make_response, jsonify
from flask_restful import Api, Resource
from flask_restful.utils import cors
from models import Department, Employee
from . import employee_bp

api = Api(employee_bp)


class AffiliationListResource(Resource):
    def get(self):
        data = Department.objects.to_json()
        return data, 200, {'Content-type': 'application/json'}


class AffiliationResource(Resource):
    def get(self, object_id):
        data = Department.objects(id=object_id).to_json()
        return data, 200, {'Content-type': 'application/json'}


class EmployeeListResource(Resource):
    def get(self):
        dept_slug = request.args.get('department_slug')
        print('dept slug is {}'.format(dept_slug))
        dept = Department.objects(slug=dept_slug).first()
        employees = Employee.objects(department=dept)
        return employees.to_json(), 200, {'Content-type': 'application/json'}


class EmployeeResource(Resource):
    def get(self, employee_id):
        emp = Employee.objects(id=employee_id).first()
        return emp.to_json(), 200, {'Content-type': 'application/json'}


class ProfileImageResource(Resource):
    def get(self, employee_id):
        emp = Employee.objects(id=employee_id).first()
        response = make_response(emp.photo.read())
        response.mimetype = emp.photo.content_type
        return response


class ResearchArticleResource(Resource):
    def post(self):
        data = request.get_json()
        if data:
            print(data)
            return jsonify(data="success")
        else:
            return jsonify(data="fail")

api.add_resource(AffiliationListResource, '/affiliations/')
api.add_resource(AffiliationResource, '/affiliations/<ObjectId:object_id>')
api.add_resource(EmployeeListResource, '/employees/')
api.add_resource(EmployeeResource, '/employees/<ObjectId:employee_id>')
api.add_resource(ProfileImageResource, '/employees/image/<ObjectId:employee_id>')
api.add_resource(ResearchArticleResource, '/employees/research/')
