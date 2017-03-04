''' Retrieve publications from Scopus APIs and add them to the database.

'''

import os
import sys
import requests
import time
import xml.etree.ElementTree as et
import re
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from collections import defaultdict

engine = create_engine('postgresql+psycopg2://likit@localhost/research_dev')
Base = automap_base()
Base.prepare(engine, reflect=True)
Session = sessionmaker(bind=engine)
session = Session()
#print(Base.classes.keys())

Abstracts = Base.classes.scopus_abstracts
Authors = Base.classes.scopus_authors
Affiliations = Base.classes.scopus_affiliations

API_KEY = '871232b0f825c9b5f38f8833dc0d8691'

ITEM_PER_PAGE = 25
SLEEPTIME = 5

def add_author(authors, abstract):
    url = 'http://api.elsevier.com/content/search/author'
    if not authors:
        return None

    for au in authors:
        params = {'apiKey': API_KEY,
                    'query': 'auid({})'.format(au['authid']),
                    'httpAccept': 'application/json'}
        author = requests.get(url, params=params).json()
        author = author['search-results']['entry'][0]
        cur_affil = author.get('affiliation-current', {})
        preferred_name=author['preferred-name']['surname']+ ' ' +\
                                    author['preferred-name']['given-name']

        new_author = Authors(initials=author['preferred-name'].get('initials', ''),
                surname=author['preferred-name'].get('surname', ''),
                given_name=author['preferred-name'].get('given-name', ''),
                preferred_name=preferred_name,
                url=author.get('prism:url', ''))
        
        # get an affiliation of the author
        new_affil = Affiliations(name=cur_affil.get('affiliation-name', ''),
                            city=cur_affil.get('affiliation-city', ''),
                            country=cur_affil.get('affiliation-country', ''),
                            scopus_affil_id=cur_affil.get('affiliation-id', ''))

        # search for the affiliation in the db
        existing_affil = session.query(Affiliations).filter_by(
                                scopus_affil_id=new_affil.scopus_affil_id).first()
        if existing_affil:
            # if the affiliation exists, get its ID
            affil_id = existing_affil.id
        else:
            # if the affiliation not exists, insert it to the db
            session.add(new_affil)
            session.commit()
            affil_id = new_affil.id

        author = session.query(Authors).filter_by(
                given_name=new_author.given_name,
                surname=new_author.surname).first()
        if not author:
            new_author.affil_id = affil_id  # assign affiliation ID to the author
            new_author.scopus_abstracts_collection.append(abstract)
            abstract.scopus_authors_collection.append(new_author)
            print('new author, {}, added.'.format(
                            new_author.preferred_name.encode('utf8')))
            session.add(new_author)
        else:
            if affil_id != author.affil_id:
                author.affil_id = affil_id  # update an affiliation

            author.scopus_abstracts_collection.append(abstract)
            abstract.scopus_authors_collection.append(author)
            print('new article added to {}'.format(
                            author.preferred_name.encode('utf8')))
            session.add(author)
        session.commit()

def update(year):
    query = 'AFFILORG("faculty of medical technology" "mahidol university")' \
                'AND PUBYEAR IS %s' % year

    params = {'apiKey': API_KEY, 'query': query, 'httpAccept': 'application/json'}
    apikey = {'apiKey' : API_KEY}
    url = 'http://api.elsevier.com/content/search/scopus'

    r = requests.get(url, params=params).json()

    total_results = int(r['search-results']['opensearch:totalResults'])
    page = 0
    article_no = 0

    print('Total articles %d' % total_results)

    for start in range(0, total_results+1, ITEM_PER_PAGE):
        page += 1
        print >> sys.stderr, \
                'Waiting %d sec to download from page %d... (%d articles/page)' \
                                            % (SLEEPTIME, page, ITEM_PER_PAGE)
        time.sleep(SLEEPTIME)
        params = {'apiKey': API_KEY,
                    'query': query,
                    'start': start,
                    'httpAccept': 'application/json',
                    'view': 'COMPLETE',
                    'count': ITEM_PER_PAGE}

        articles = requests.get(url, params=params).json()['search-results']['entry']
        for n, entry in enumerate(articles, start=1):
            article_no += 1

            print >> sys.stderr, '%d) %s..%s' \
                    % (article_no, entry['dc:title'][:80], entry['dc:creator'][:30])

            new_abstract = Abstracts(url=entry.get('prism:url', ''),
                                    title=entry.get('dc:title', ''),
                                    identifier=entry.get('dc:identifier', ''),
                                    pii=entry.get('pii', ''),
                                    doi=entry.get('prism:doi', ''),
                                    eid=entry.get('eid', ''),
                                    publication_name=entry.get('prism:publicationName', ''),
                                    citedby_count=entry.get('citedby-count', ''),
                                    cover_date=entry.get('prism:coverDate', ''),
                                    description=entry.get('dc:description', '')
                                    )
            existing_abstract = session.query(Abstracts).filter_by(
                                    doi=entry.get('prism:doi')).first()
            if existing_abstract:
                print('Article already in the database.')
            else:
                print('New article loaded.')
                session.add(new_abstract)
                session.flush()
                add_author(entry.get('author'), new_abstract)
    session.commit()


if __name__=='__main__':
    year = int(sys.argv[1])
    entry = update(year)