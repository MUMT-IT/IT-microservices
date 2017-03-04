from main import db
from flask import jsonify
from . import research_bp as research
from flask_cors import cross_origin
from models import ScopusAbstract
from sqlalchemy import and_

@research.route('/abstracts/')
@cross_origin()
def get_abstracts():
    all_abstracts = {}
    for year in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]:
        start_date = '%d-01-01' % year
        end_date = '%d-12-31' % year
        abstracts = ScopusAbstract.query.filter(and_(ScopusAbstract.cover_date>=start_date,
                                                        ScopusAbstract.cover_date<=end_date))
        all_abstracts[year] = len([abs for abs in abstracts])

    d = []
    for k,v in all_abstracts.iteritems():
        d.append({'year': k, 'value': v})

    d = sorted(d, key=lambda x: x['year'])

    return jsonify({'data': d})
    
@research.route('/abstracts/<int:year>')
@cross_origin()
def get_abstracts_by_year(year):
    start_date = '%d-01-01' % year
    end_date = '%d-12-31' % year
    abstracts = ScopusAbstract.query.filter(and_(ScopusAbstract.cover_date>=start_date,
                                                    ScopusAbstract.cover_date<=end_date))
    d = []
    for abs in abstracts:
        authors = [] 
        for au in abs.authors:
            authors.append({'name': au.preferred_name, 'affil': au.affiliation.name})
        d.append({'id': abs.id, 'title': abs.title, 'authors': authors, 'cover_date': abs.cover_date, 'journal': abs.publication_name})

    d = sorted(d, key=lambda x: x['cover_date'])

    return jsonify({'data': d})