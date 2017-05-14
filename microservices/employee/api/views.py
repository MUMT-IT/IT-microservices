from flask_restful import Api, Resource
from flask_restful.utils import cors
from models import Department, Employee
from . import employee_bp

api = Api(employee_bp)


class AffiliationListResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        data = Department.objects.to_json()
        return data, 200, {'Content-type': 'application/json'}


class AffiliationResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self, object_id):
        data = Department.objects(id=object_id).to_json()
        return data, 200, {'Content-type': 'application/json'}


api.add_resource(AffiliationListResource, '/affiliations/')
api.add_resource(AffiliationResource, '/affiliations/<ObjectId:object_id>')
