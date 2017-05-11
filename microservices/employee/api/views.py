from flask import jsonify, request
from flask_restful import Api, Resource
from . import employee_bp
from models import Employee, Affiliation, EmployeeSchema, AffiliationSchema
from flask_restful.utils import cors

api = Api(employee_bp)

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

affils_schema = AffiliationSchema(many=True)

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

    @cors.crossdomain(origin='*')
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, 400
        errors = employee_schema.validate(request_dict)
        if errors:
            return errors, 400
        else:
            try:
                empl = Employee(
                    first_th=request_dict['firstTH'],
                    last_th=request_dict['lastTH'],
                    first_en=request_dict['firstEN'],
                    last_en=request_dict['lastEN'],
                    date_of_birth=request_dict['dob'],
                    employed_date=request_dict['employedDate'],
                    email=request_dict['email'],
                    affiliation_id=request_dict['affilID'],
                    license_plate=request_dict['licensePlate'],
                    office_id=1,
                    cellphone=request_dict['cellphone']
                )
                db.session.add(empl)
                db.session.commit()
                return {'status': 'success'}, 201
            except SQLAlchemyError, e:
                db.session.rollback()
                resp = jsonify({'error': str(e)})
                return resp, 400
        return jsonify(request_dict)

class AffiliationListResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        affils = Affiliation.query.all()
        result = affils_schema.dump(affils).data
        return jsonify({'affils': result})

api.add_resource(AffiliationListResource, '/affils/')
api.add_resource(EmployeeResource, '/employees/<int:id>')
api.add_resource(EmployeeListResource, '/employees/')