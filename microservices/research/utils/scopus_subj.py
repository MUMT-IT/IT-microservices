import sys
import requests
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://likit@localhost/research_dev')
Base = automap_base()
Base.prepare(engine, reflect=True)
Session = sessionmaker(bind=engine)
session = Session()
ScopusSubjArea = Base.classes.scopus_subj_areas

API_KEY = '871232b0f825c9b5f38f8833dc0d8691'

# https://api.elsevier.com/documentation/search/SCOPUSSearchTips.htm

def main(affil, abbr, year):
    subj_areas = {'COMP': 0, 'CENG': 0, 'CHEM': 0,
                    'PHAR': 0, 'AGRI': 0, 'ARTS': 0,
                    'BIOC': 0, 'BUSI': 0, 'DECI': 0,
                    'DENT': 0, 'EART': 0, 'ECON': 0,
                    'ENER': 0, 'ENGI': 0, 'ENVI': 0,
                    'HEAL': 0, 'IMMU': 0, 'MATE': 0,
                    'MATH': 0, 'MEDI': 0, 'NEUR': 0,
                    'NURS': 0, 'PHYS': 0, 'PSYC': 0,
                    'SOCI': 0, 'VETE': 0, 'MULT': 0}
    citations = {'COMP': 0, 'CENG': 0, 'CHEM': 0,
                    'PHAR': 0, 'AGRI': 0, 'ARTS': 0,
                    'BIOC': 0, 'BUSI': 0, 'DECI': 0,
                    'DENT': 0, 'EART': 0, 'ECON': 0,
                    'ENER': 0, 'ENGI': 0, 'ENVI': 0,
                    'HEAL': 0, 'IMMU': 0, 'MATE': 0,
                    'MATH': 0, 'MEDI': 0, 'NEUR': 0,
                    'NURS': 0, 'PHYS': 0, 'PSYC': 0,
                    'SOCI': 0, 'VETE': 0, 'MULT': 0}
    query = 'AFFILORG(%s)' \
                'AND PUBYEAR IS %s' % (affil, year)

    params = {'apiKey': API_KEY, 'query': query, 'httpAccept': 'application/json'}
    url = 'http://api.elsevier.com/content/search/scopus'

    for subj in subj_areas:
        params['subj'] = subj
        r = requests.get(url, params=params).json()
        total_results = int(r['search-results']['opensearch:totalResults'])
        subj_areas[subj] = total_results
        for a in r['search-results']['entry']:
            cite = a.get('citedby-count', '')
            if cite != '':
                citations[subj] += int(cite)

    for subj in subj_areas:
        a = ScopusSubjArea(year=year, area=subj,
                            articles=subj_areas[subj],
                            affil_abbr=abbr,
                            citations=citations[subj])
        session.add(a)
    session.commit()

if __name__=='__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])