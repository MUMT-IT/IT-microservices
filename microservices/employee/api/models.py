from main import me


class Department(me.Document):
    name_th = me.StringField()
    name_en = me.StringField()
    head = me.ReferenceField('Employee')
    meta = {'collection': 'departments'}


class Contact(me.EmbeddedDocument):
    building_name_th = me.StringField()
    building_name_en = me.StringField()
    building_campus_th = me.StringField()
    building_campus_en = me.StringField()
    building_address = me.StringField()
    office_number = me.StringField()
    phone_number = me.ListField(me.StringField())
    cellphone = me.StringField()
    email = me.EmailField(required=True)


class UpdateLog(me.EmbeddedDocument):
    updated_by = me.ReferenceField('Employee')
    updated_at = me.DateTimeField()


class Employee(me.Document):
    first_name_th = me.StringField(max_length=60)
    last_name_th = me.StringField(max_length=80)
    first_name_en = me.StringField(max_length=60)
    last_name_en = me.StringField(max_length=80)
    dob = me.DateTimeField()
    employed_date = me.DateTimeField()
    affl_id = me.ReferenceField('Department')
    affl_name_en = me.StringField()
    affl_name_th = me.StringField()
    contact = me.EmbeddedDocumentField(Contact)
    update_logs = me.ListField(me.EmbeddedDocumentField('UpdateLog'))
    added_by = me.ReferenceField('Employee')
    added_at = me.DateTimeField()

    meta = {'allow_inheritance': True, 'collection': 'employees'}

