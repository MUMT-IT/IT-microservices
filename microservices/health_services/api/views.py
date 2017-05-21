# -*- coding:utf8 -*-
import gspread
import httplib2
from .drive import get_file_list, get_credentials_from_file
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from . import healthservice_blueprint as healthservice
from sqlalchemy import create_engine, MetaData, Table, select, func
from flask import jsonify
from flask_cors import cross_origin
from collections import defaultdict
from models import ServicedCustomers, ServiceCenter

engine = create_engine('postgresql+psycopg2://likit@localhost/healthdw_dev',
                        convert_unicode=True)

metadata = MetaData(bind=engine)
con = engine.connect()

facts = Table('facts', metadata, autoload=True)
dates = Table('dates', metadata, autoload=True)
companies = Table('companies', metadata, autoload=True)


@healthservice.route('/customers/count/')
@cross_origin(origin='*')
def get_annual_customers():
    data = []
    for year in range(2007,2018):
        s = select([func.count(facts.c.customer_id.distinct())])
        s = s.select_from(facts.join(dates)).where(facts.c.service_date_id==dates.c.date_id)
        s = s.where(dates.c.gregorian_year==year)
        rp = con.execute(s)
        data.append(dict(year=year, count=rp.scalar()))
    return jsonify({'data': data})


@healthservice.route('/customers/companies/engagement/')
@cross_origin(origin='*')
def get_companies_engagement_rate():
    data = []
    total_counts = defaultdict(int)
    for year in range(2008, 2018):
        counts = []
        s = select([companies.c.name.distinct()])
        s = s.select_from(facts.join(dates).join(companies))
        s = s.where(facts.c.service_date_id==dates.c.date_id)
        s = s.where(facts.c.company_id==companies.c.company_id)
        s = s.where(dates.c.gregorian_year==year)
        rp = con.execute(s)
        for c in rp:
            total_counts[c[companies.c.name]] += 1
            counts.append({
                'company': c[companies.c.name],
                'count': total_counts[c[companies.c.name]]
            })
        data.append(dict(year=year, value=counts))
    return jsonify(data=data)


@healthservice.route('/gdrive/customers/update/')
def udpate_wrs():
    '''Load data from Wellrounded scholar spreadsheet to DB'''
    cred = get_credentials_from_file()  # get_credentials func cannot run
    # inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    folder_id = '0B45WRw4HPnk_cnhXZDhOaGlrejQ'
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = \
        ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    records = {}
    medilab = ServiceCenter.objects(slug="medilab-center").first()
    toxicology = ServiceCenter.objects(slug="toxicology").first()
    chromosome = ServiceCenter.objects(slug="chromosome").first()
    mobile = ServiceCenter.objects(slug="mobile-unit").first()
    gjmt = ServiceCenter.objects(slug="gjmt").first()
    gjrt = ServiceCenter.objects(slug="gjrt").first()
    for f in files:
        file_name, file_id = f['name'], f['id']
        print('Loading data from file: {} {}'.format(file_name, file_id))
        wks = gc.open_by_key(file_id).get_worksheet(0)
        for c in range(2,10):
            data = wks.col_values(c)[2:11]
            for i in range(len(data)):
                try:
                    data[i] = float(data[i])
                except:
                    data[i] = 0

            _ = ServicedCustomers(year=int(data[0]), center=medilab,
                                  customers=data[1])
            _.save()
            _ = ServicedCustomers(year=int(data[0]), center=mobile,
                                  customers=data[3])
            _.save()
            _ = ServicedCustomers(year=int(data[0]), center=toxicology,
                                  customers=data[4])
            _.save()
            _ = ServicedCustomers(year=int(data[0]), center=chromosome,
                                  customers=data[5])
            _.save()
            _ = ServicedCustomers(year=int(data[0]), center=gjmt,
                                  customers=data[7])
            _.save()
            _ = ServicedCustomers(year=int(data[0]), center=gjrt,
                                  customers=data[8])
            _.save()
    return jsonify(message='fuck')


@healthservice.route('/gdrive/files/')
@cross_origin()
def get_gdrive_file_list():
    cred = get_credentials_from_file()  # get_credentials func cannot run inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(pageSize=10,
                                   fields="nextPageToken, files(id, name, parents)").execute()
    items = results.get('files', [])
    if not items:
        return jsonify({'files': [], 'message': 'No files found.'})
    else:
        files = []
        for item in items:
            files.append({'id': item['id'], 'name': item['name'], 'parents': item.get('parents', '')})
            #print('{0} ({1})'.format(item['name'], item['id']))
        return jsonify({'files': files})


@healthservice.route('/gdrive/customers/stats/')
@cross_origin()
def get_customers_stat():
    data = []
    years = defaultdict(list)
    for s in ServicedCustomers.objects:
        d = {
            'customers' : s.customers,
            'year': s.year,
            'center_slug': s.center.slug
        }
        years[d['year']].append(d)
    for yrs in years:
        data.append({
            'year': yrs,
            'data': years[yrs]
        })
    return jsonify(data)
