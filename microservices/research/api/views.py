from main import db
from flask import jsonify, request
from . import research_bp as research
from flask_cors import cross_origin
from models import ScopusAbstract, ScopusSubjArea, ScopusAuthor
from sqlalchemy import and_
from itertools import groupby


@research.route('/abstracts/numbers')
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


@research.route('/abstracts/list')
@cross_origin()
def get_abstracts_by_year():
    d = []
    for abs in db.session.query(ScopusAbstract):
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


@research.route('/abstracts/authors/')
@cross_origin()
def get_abstracts_by_author():
    given_name = request.args.get('first_name')
    surname = request.args.get('last_name')
    if given_name and surname:
        author = ScopusAuthor.query.filter(and_(ScopusAuthor.surname==surname,
                                    ScopusAuthor.given_name==given_name)).first()
    elif surname:
        author = ScopusAuthor.query.filter(ScopusAuthor.surname==surname).first()
    elif given_name:
        author = ScopusAuthor.query.filter(ScopusAuthor.given_name==given_name).first()
    else:
        return jsonify(data={'error': 'no first name and last name given.'})

    if not author:
        return jsonify(data={'error': 'author not found'})

    papers = []
    for p in author.abstracts:
        abs_authors = []
        for au in p.authors:
            abs_authors.append({
                'name': au.preferred_name, 'affil': au.affiliation.name
            })
        papers.append({
            'id': p.id,
            'title': p.title,
            'doi': p.doi,
            'publication_name': p.publication_name,
            'citedby_count': p.citedby_count,
            'cover_date': p.cover_date,
            'authors': abs_authors,
            'description': p.description
        })
    return jsonify(data=papers)
