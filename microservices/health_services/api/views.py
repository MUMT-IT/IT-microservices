from . import healthservice_blueprint as healthservice
from sqlalchemy import create_engine, MetaData, Table, select, func
from flask import jsonify
from flask_cors import cross_origin

engine = create_engine('postgresql+psycopg2://likit@localhost/healthdw_dev',
                        convert_unicode=True)

metadata = MetaData(bind=engine)
con = engine.connect()

facts = Table('facts', metadata, autoload=True)
dates = Table('dates', metadata, autoload=True)


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