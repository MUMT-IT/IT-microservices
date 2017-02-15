from main import db, ma
from marshmallow import fields

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_th = db.Column(db.String(80), nullable=False)
    first_en = db.Column(db.String(80), nullable=False)
    last_th = db.Column(db.String(80), nullable=False)
    last_en = db.Column(db.String(80), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    employed_date = db.Column(db.DateTime, nullable=True)
    affiliation_id = db.Column(db.Integer, nullable=False)
    office_id = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(40))
    license_plate = db.Column(db.String(40))
    cellphone = db.Column(db.String(16))


class EmployeeSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    first_th = fields.String(required=True)
    first_en = fields.String(required=True)
    last_th = fields.String(required=True)
    last_en = fields.String(required=True)
    date_of_birth = fields.DateTime()
    employed_date = fields.DateTime()
    affiliation_id = fields.Integer()
    office_id = fields.Integer()
    email = fields.String()
    license_plate = fields.String()
    cellphone = fields.String()