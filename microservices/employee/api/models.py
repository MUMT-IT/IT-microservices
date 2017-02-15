from main import db

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