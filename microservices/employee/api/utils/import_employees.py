import pandas
from pandas import read_excel
from datetime import datetime
from ..models import Employee, Contact, UpdateLog, Department, Lecturer


def import_data(excel_filename):
    wb = read_excel(excel_filename, header=0)
    wb = wb.where(pandas.notnull(wb), None)
    for idx, row in wb.iterrows():
        email = row['email']
        if Employee.objects(email=email).first():
            continue  # skip existing employee

        first_name_en = row['first_name_en']
        last_name_en = row['last_name_en']
        first_name_th = row['first_name_th']
        last_name_th = row['last_name_th']
        dob = row['dob']
        employed_date = row['employed_date']
        department_slugs = row['department']
        photo_file = row['photo']
        building_name_en = row['building_name_en']
        building_name_th = row['building_name_th']
        building_campus_en = row['building_campus_en']
        building_campus_th = row['building_campus_th']
        building_address_en = row['building_address_en']
        building_address_th = row['building_address_th']
        office_number = row['office_number']
        cellphone = row['cellphone']
        academic_title = row['academic_title']
        degree = row['degree']
        added_by = row['added_by']
        phone_number = row['phone_number']
        phone_number = str(phone_number).split(',') if phone_number else []
        adder = Employee.objects(email=added_by).first()
        contact = Contact(office_number=str(office_number),
                          phone_number=phone_number,
                          cellphone=str(cellphone),
                          building_name_en=building_name_en,
                          building_name_th=building_name_th,
                          building_campus_en=building_campus_en,
                          building_campus_th=building_campus_th,
                          building_address_en=building_address_en,
                          building_address_th=building_address_th)
        update = [UpdateLog(updated_by=adder)]
        departments = []
        for slug in department_slugs.split(','):
            departments.append(Department.objects(slug=slug).first())
        lecturer = Lecturer(first_name_en=first_name_en,
                            last_name_en=last_name_en,
                            first_name_th=first_name_th,
                            last_name_th=last_name_th,
                            email=email,
                            dob=dob,
                            employed_date=employed_date,
                            academic_title=academic_title,
                            highest_degree=degree,
                            contact=contact,
                            department=departments,
                            added_by=adder,
                            update_logs=update
                            )
        if photo_file:
            lecturer.photo.put(open(photo_file, 'rb'), content_type='image/jpg')
        lecturer.save()
