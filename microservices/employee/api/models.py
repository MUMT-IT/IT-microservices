import datetime
from main import me


class Department(me.Document):
    name_th = me.StringField()
    name_en = me.StringField()
    head = me.ReferenceField('Employee')
    slug = me.StringField(unique=True)
    meta = {'collection': 'departments'}


class Contact(me.EmbeddedDocument):
    building_name_th = me.StringField()
    building_name_en = me.StringField()
    building_campus_th = me.StringField()
    building_campus_en = me.StringField()
    building_address_en = me.StringField()
    building_address_th = me.StringField()
    office_number = me.StringField()
    phone_number = me.ListField(me.StringField())
    cellphone = me.StringField()


class UpdateLog(me.EmbeddedDocument):
    updated_by = me.ReferenceField('Employee')
    updated_at = me.DateTimeField(default=datetime.datetime.now)


class Employee(me.Document):
    email = me.EmailField(required=True, unique=True)
    first_name_th = me.StringField(max_length=60)
    last_name_th = me.StringField(max_length=80)
    first_name_en = me.StringField(max_length=60)
    last_name_en = me.StringField(max_length=80)
    dob = me.DateTimeField()  # date of birth
    employed_date = me.DateTimeField()
    department = me.ListField(me.ReferenceField('Department'), default=[])  # dept. includes dept., unit, center and so on.
    photo = me.FileField()
    contact = me.EmbeddedDocumentField(Contact)
    update_logs = me.ListField(me.EmbeddedDocumentField('UpdateLog'))
    added_by = me.ReferenceField('self')
    added_at = me.DateTimeField(default=datetime.datetime.now)

    meta = {'allow_inheritance': True, 'collection': 'employees'}


class Lecturer(Employee):
    academic_title = me.StringField()
    highest_degree = me.IntField()


class ResearchArticle(me.Document):
    title = me.StringField(required=True)
    authors = me.ListField(me.ReferenceField('Employee'))
    status = me.StringField()
    author_list = me.StringField()
    cover_date = me.DateTimeField()
    publisher = me.StringField()

