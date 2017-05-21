import datetime
from main import me


class ServiceCenter(me.Document):
    name_th = me.StringField()
    name_en = me.StringField()
    slug = me.StringField(unique=True)


class ServicedCustomers(me.Document):
    center = me.ReferenceField('ServiceCenter')
    year = me.IntField()
    customers = me.IntField()

