from main import db
from flask import jsonify
from . import research_bp as research
from flask_cors import cross_origin
from models import ScopusAbstract, ScopusSubjArea
from sqlalchemy import and_
from itertools import groupby

@research.route('/abstracts/')
@cross_origin()
def get_abstracts():
    all_abstracts = {}
    sum_citations = {}
    citations = {}
    #TODO: reads years automatically from the database
    for year in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]:
        start_date = '%d-01-01' % year
        end_date = '%d-12-31' % year
        abstracts = ScopusAbstract.query.filter(and_(ScopusAbstract.cover_date>=start_date,
                                                        ScopusAbstract.cover_date<=end_date))
        all_abstracts[year] = len([abs for abs in abstracts])
        citations[year] = [abs.citedby_count for abs in abstracts]
        sum_citations[year] = sum(citations[year])

    d = []
    c = []
    for k,v in all_abstracts.iteritems():
        d.append({'year': k, 'value': v})

    for k,v in sum_citations.iteritems():
        c.append({'year': k, 'value': v})

    d = sorted(d, key=lambda x: x['year'])
    c = sorted(c, key=lambda x: x['year'])

    return jsonify({'articles': d, 'citations': c})
    
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
        d.append({'id': abs.id, 'title': abs.title, 'authors': authors,
                    'cover_date': abs.cover_date, 'journal': abs.publication_name,
                    'abstract': abs.description, 'citedby_count': abs.citedby_count,
                    'url': abs.url})

    d = sorted(d, key=lambda x: x['cover_date'])

    return jsonify({'data': d})


@research.route('/abstracts/subject_areas/')
@cross_origin()
def get_abstracts_by_subject_area():
    years = range(2010, 2018)
    results = {}
    for year in years:
        data = ScopusSubjArea.query.filter(ScopusSubjArea.year==str(year))
        for d in data:
            if year not in results:
                results[year] = []
            else:
                results[year].append({'affil': d.affil_abbr,
                                        'area': d.area,
                                        'articles': d.articles,
                                        'citations': d.citations})
    return jsonify(results)
