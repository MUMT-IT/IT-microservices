import json
from datetime import datetime
from flask import request, make_response, jsonify
from flask_restful import Api, Resource
from flask_restful.utils import cors
from flask_cors import cross_origin
from models import Department, Employee, ResearchArticle
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


class EmployeeListResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        dept_slug = request.args.get('department_slug')
        print('dept slug is {}'.format(dept_slug))
        dept = Department.objects(slug=dept_slug).first()
        employees = Employee.objects(department=dept)
        return employees.to_json(), 200, {'Content-type': 'application/json'}


class EmployeeResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self, employee_id):
        emp = Employee.objects(id=employee_id).first()
        return emp.to_json(), 200, {'Content-type': 'application/json'}


class ProfileImageResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self, employee_id):
        emp = Employee.objects(id=employee_id).first()
        response = make_response(emp.photo.read())
        response.mimetype = emp.photo.content_type
        return response


class ResearchArticleResource(Resource):
    @cross_origin
    def post(self):
        data = request.get_json()
        authors = data['authors'].split(',')
        cdate = datetime.strptime(data['cover_date'], '%Y-%m-%d')
        article = ResearchArticle(title=data['title'],
                                    publisher=data['publisher'],
                                    author_list=data['authors'],
                                    status=data['status'],
                                    cover_date=cdate
                                  )
        article_authors = []
        for au in authors:
            au = au.lstrip().rstrip()  # trim whitespaces
            fname, lname = au.split()
            e = Employee.objects(__raw__={'first_name_en': fname, 'last_name_en': lname}).first()
            if e:
                article_authors.append(e)
            else:
                continue
        article.authors = article_authors
        article.save()
        return jsonify(data="success")


class ResearchArticleListResource(Resource):
    @cors.crossdomain(origin='*')
    def get(self, employee_id):
        emp = Employee.objects(id=employee_id).first()
        articles = ResearchArticle.objects(authors=emp)
        return articles.to_json(), 200, {'Content-type': 'application/json'}



api.add_resource(AffiliationListResource, '/affiliations/')
api.add_resource(AffiliationResource, '/affiliations/<ObjectId:object_id>')
api.add_resource(EmployeeListResource, '/employees/')
api.add_resource(EmployeeResource, '/employees/<ObjectId:employee_id>')
api.add_resource(ProfileImageResource, '/employees/image/<ObjectId:employee_id>')
api.add_resource(ResearchArticleResource, '/employees/research/')
api.add_resource(ResearchArticleListResource, '/employees/research/<ObjectId:employee_id>')
