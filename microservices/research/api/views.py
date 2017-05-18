from main import db
from flask import jsonify, request
from . import research_bp as research
from flask_cors import cross_origin
from models import ScopusAbstract, ScopusSubjArea, ScopusAuthor, ScopusAbstractCount
from sqlalchemy import and_
from collections import defaultdict


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


@research.route('/abstracts/list/<int:year>')
@cross_origin()
def get_abstracts_by_year(year):
    d = []
    for abs in db.session.query(ScopusAbstract):
        if abs.cover_date.year == year:
            authors = []
            for au in abs.authors:
                authors.append({'first_name': au.given_name, 'last_name': au.surname})
            d.append({'id': abs.id, 'title': abs.title, 'authors': authors,
                'cover_date': abs.cover_date, 'journal': abs.publication_name,
                'abstract': abs.description, 'citedby_count': abs.citedby_count,
                'url': abs.url})

    d = sorted(d, key=lambda x: x['cover_date'])

    return jsonify({'data': d})


@research.route('/abstracts/list')
@cross_origin()
def get_abstracts_all_years():
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
    years = range(2013, 2018)
    results = []
    for year in years:
        num_articles = []
        data = ScopusSubjArea.query.filter(ScopusSubjArea.year==str(year))
        for d in data:
            num_articles.append({'affil': d.affil_abbr,
                                    'area': d.area,
                                    'articles': d.articles,
                                    'citations': d.citations})
        results.append({'year': year, 'counts': num_articles})
    return jsonify(results)


@research.route('/abstracts/authors/')
@cross_origin()
def get_abstracts_by_author():
    given_name = request.args.get('first_name')
    surname = request.args.get('last_name')
    year = request.args.get('year')
    if given_name and surname:
        author = ScopusAuthor.query.filter(and_(ScopusAuthor.surname==surname,
                                        ScopusAuthor.given_name==given_name)).first()
    elif surname:
        author = ScopusAuthor.query.filter(ScopusAuthor.surname==surname).first()
    elif given_name:
        author = ScopusAuthor.query.filter(ScopusAuthor.given_name==given_name).first()
    else:
        return jsonify(data=[])

    if not author:
        return jsonify(data=[])

    papers = []
    for p in author.abstracts:
        if year:
            if p.cover_date.year != int(year):
                continue

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
    print(len(papers))
    return jsonify(data=papers)


@research.route('/abstracts/benchmark/numbers/')
@cross_origin()
def get_abstracts_benchmark():
    data = defaultdict(list);
    for abs in db.session.query(ScopusAbstractCount):
        d = {
            'institute': abs.institute,
            'year': abs.year,
            'articles': abs.articles,
            'citations': abs.citations
        }
        data[abs.institute].append(d)

    dat = []
    for inst in data:
        data[inst] = sorted(data[inst], key=lambda x: x['year'])
        dat.append({'institute': inst, 'counts': data[inst]})
    return jsonify(dat)
