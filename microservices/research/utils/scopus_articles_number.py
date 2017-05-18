import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://likit@localhost/research_dev')
Base = automap_base()
Base.prepare(engine, reflect=True)
Session = sessionmaker(bind=engine)
session = Session()
ScopusArticleCounts = Base.classes.abstract_count

API_KEY = '871232b0f825c9b5f38f8833dc0d8691'

def main(affil, abbr, start_year, end_year):
    for year in range(int(start_year), int(end_year)):
        print('Download articles of the year {}...'.format(year))
        query = 'AFFILORG(%s)' \
                'AND PUBYEAR IS %s' % (affil, year)

        params = {'apiKey': API_KEY, 'query': query, 'httpAccept': 'application/json'}
        url = 'http://api.elsevier.com/content/search/scopus'

        print('Sending request to Scopus...')
        r = requests.get(url, params=params).json()
        citations = 0
        total_results = int(r['search-results']['opensearch:totalResults'])
        for a in r['search-results']['entry']:
            cite = a.get('citedby-count', '')
            if cite != '':
                citations += int(cite)

        acount = ScopusArticleCounts(institute=abbr,
                        year=int(year), articles=total_results, citations=citations)
        session.add(acount)
    session.commit()

if __name__=='__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
