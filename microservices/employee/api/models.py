from main import me


class EmployeeAffiliation(me.Document):
    name_th = me.StringField()
    name_en = me.StringField()
    # meta = {'collection': 'empl_affil'}  # to manually set a collection name


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


class Employee(me.Document):
    first_name_th = me.StringField(max_length=60)
    last_name_th = me.StringField(max_length=80)
    first_name_en = me.StringField(max_length=60)
    last_name_en = me.StringField(max_length=80)
    dob = me.DateTimeField()
    employed_date = me.DateTimeField()
    affl_id = me.ReferenceField(EmployeeAffiliation)
    affl_name_en = me.StringField()
    affl_name_th = me.StringField()
    contact = me.EmbeddedDocumentField(Contact)

    meta = {'allow_inheritance': True}

