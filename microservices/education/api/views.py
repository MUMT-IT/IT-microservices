# -*- coding:utf8 -*-
import gspread
import httplib2
import numpy as np

from collections import defaultdict

from flask import jsonify, request, redirect, session
from . import education_bp as education
from .drive import get_file_list, get_credentials_from_file
from apiclient import discovery
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials
from flask_cors import cross_origin
from main import db
from models import (SurveyCategory, SurveyAnswer,
                        SurveyWRSSummary, SurveyWRSTeachingSummary,
                        SurveyQuestion, FollowUpSummary,
                        AcademicProgram)


@education.route('/gdrive/files/')
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


@education.route('/gdrive/wrs/update/')
def udpate_wrs():
    '''Load data from Wellrounded scholar spreadsheet to DB'''
    cred = get_credentials_from_file()  # get_credentials func cannot run 
                                        # inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    folder_id = '0B45WRw4HPnk_T3ctb3Q1eHRhczA'
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = \
            ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    records = {}
    for f in files:
        file_name, file_id = f['name'], f['id']
        year = file_name.split('.')[0]
        if SurveyWRSSummary.query.filter_by(year=year).first():
            print('Data of year {} already exists'.format(year))
            continue
        print('Loading data from file: {}'.format(file_name))
        try:
            wks = gc.open_by_key(file_id).sheet1
        except:
            batch = service.new_batch_http_request()
            user_permission = {
                'type': 'user',
                'role': 'onwer',
                'emailAddress': 'academic-affairs-mumt@academic-affairs.iam.gserviceaccount.com'
                }
            batch.add(service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields='id',
            ))
            batch.execute()
            wks = gc.open_by_key(file_id).sheet1
        else:
            wrs_category = \
                SurveyCategory.query.filter_by(name="wellrounded scholar").first()
            wks = gc.open_by_key(file_id).sheet1
            prior_knowledge = wks.col_values(13)[1:]
            prior_prof_skill = wks.col_values(14)[1:]
            prior_creativity = wks.col_values(15)[1:]
            prior_analysis = wks.col_values(16)[1:]
            prior_leadership = wks.col_values(17)[1:]
            prior_social_resp = wks.col_values(18)[1:]
            post_knowledge = wks.col_values(19)[1:]
            post_prof_skill = wks.col_values(20)[1:]
            post_creativity = wks.col_values(21)[1:]
            post_analysis = wks.col_values(22)[1:]
            post_leadership = wks.col_values(23)[1:]
            post_social_resp = wks.col_values(24)[1:]
            learning_methods = ['lecture', 'lab', 'buzzgroup', 'casestudy',
                                'discussion', 'roleplay', 'workgroup',
                                'fieldtrip', 'community', 'pbl',
                                'transformative', 'project', 'intern'
                                ]
            j = 0
            teaching_wrs_results = {}
            for i in range(35,113,6):
                lm = learning_methods[j]
                teaching_wrs_results[lm] = defaultdict(dict)
                teaching_wrs_results[lm]['knowledge'] = wks.col_values(i)[1:]
                teaching_wrs_results[lm]['prof_skill'] = wks.col_values(i+1)[1:]
                teaching_wrs_results[lm]['creativity'] = wks.col_values(i+2)[1:]
                teaching_wrs_results[lm]['analysis'] = wks.col_values(i+3)[1:]
                teaching_wrs_results[lm]['leadership'] = wks.col_values(i+4)[1:]
                teaching_wrs_results[lm]['socialresp'] = wks.col_values(i+5)[1:]
                j += 1
                
            i = 0
            while True:
                if(prior_knowledge[i] == '' and prior_prof_skill[i] == '' and
                    prior_creativity[i] == '' and prior_analysis[i] == '' and
                    prior_leadership[i] == '' and prior_social_resp[i] == ''):
                    break
                i += 1
            prior_knowledge = [int(d) for d in prior_knowledge[:i]]
            prior_prof_skill = [int(d) for d in prior_prof_skill[:i]]
            prior_creativity = [int(d) for d in prior_creativity[:i]]
            prior_analysis = [int(d) for d in prior_analysis[:i]]
            prior_leadership = [int(d) for d in prior_leadership[:i]]
            prior_social_resp = [int(d) for d in prior_social_resp[:i]]
            post_knowledge = [int(d) for d in prior_knowledge[:i]]
            post_prof_skill = [int(d) for d in post_prof_skill[:i]]
            post_creativity = [int(d) for d in post_creativity[:i]]
            post_analysis = [int(d) for d in post_analysis[:i]]
            post_leadership = [int(d) for d in post_leadership[:i]]
            post_social_resp = [int(d) for d in post_social_resp[:i]]

            for lm,res in teaching_wrs_results.iteritems():
                for k,v in res.iteritems():
                    #print('before ', len(teaching_wrs_results[lm][k]))
                    teaching_wrs_results[lm][k] = [int(d) for d in v[:i] if d != '']
                    #print('after ', len(teaching_wrs_results[lm][k]))

            prior = {
                'knowledge': np.mean(prior_knowledge),
                'prof_skill': np.mean(prior_prof_skill),
                'creativity': np.mean(prior_creativity),
                'analysis': np.mean(prior_analysis),
                'leadership': np.mean(prior_leadership),
                'socialresp': np.mean(prior_social_resp)
                }
            post = {
                'knowledge': np.mean(post_knowledge),
                'prof_skill': np.mean(post_prof_skill),
                'creativity': np.mean(post_creativity),
                'analysis': np.mean(post_analysis),
                'leadership': np.mean(post_leadership),
                'socialresp': np.mean(post_social_resp)
            }
            for k,v in prior.iteritems():
                a = SurveyWRSSummary(category_id=wrs_category.id,
                                question=k, value=str(v), year=year, post=False)
                db.session.add(a)
            for k,v in post.iteritems():
                a = SurveyWRSSummary(category_id=wrs_category.id,
                                question=k, value=str(v), year=year, post=True)
                db.session.add(a)
            for lm,res in teaching_wrs_results.iteritems():
                for k,v in res.iteritems():
                    a = SurveyWRSTeachingSummary(category_id=wrs_category.id,
                            question=k, method=lm, year=year,
                            value=str(np.mean(teaching_wrs_results[lm][k])))
                    db.session.add(a)
            db.session.commit()
    return jsonify({'status': 'success'}), 200

@education.route('/wrs/results/development/')
@cross_origin()
def get_wrs_results():
    wrs_category = \
        SurveyCategory.query.filter_by(name="wellrounded scholar").first()
    data = []
    for item in SurveyWRSSummary.query.with_entities(SurveyWRSSummary.year)\
                                .filter_by(category_id=wrs_category.id)\
                                .order_by(SurveyWRSSummary.year).distinct():
        year = item[0]
        res = []
        for rec in SurveyWRSSummary.query.filter_by(category_id=wrs_category.id, year=year):
            res.append({'question': rec.question, 'value': rec.value, 'post': rec.post})
        d = {'year': year}
        d['results'] = res
        data.append(d)

    return jsonify({'data': data})


@education.route('/wrs/results/teaching/')
@cross_origin()
def get_wrs_teaching_results():
    wrs_category = \
        SurveyCategory.query.filter_by(name="wellrounded scholar").first()
    learning_methods = ['lecture', 'lab', 'buzzgroup', 'casestudy',
                        'discussion', 'roleplay', 'workgroup',
                        'fieldtrip', 'community', 'pbl',
                        'transformative', 'project', 'intern'
                        ]
    data = []
    for item in SurveyWRSTeachingSummary.query.with_entities(SurveyWRSTeachingSummary.year)\
                                .filter_by(category_id=wrs_category.id)\
                                .order_by(SurveyWRSTeachingSummary.year).distinct():
        year = item[0]
        d = {'year': year, 'results': []}
        for lm in learning_methods:
            dd = {'method': lm}
            res = []
            for rec in SurveyWRSTeachingSummary.query\
                    .filter_by(category_id=wrs_category.id, year=year, method=lm):
                res.append({'question': rec.question, 'value': rec.value})
            dd['results'] = sorted(res, key=lambda x: x['question'])
            d['results'].append(dd)
        data.append(d)

    return jsonify({'data': data})


@education.route('/gdrive/followup/update/')
def udpate_followup():
    '''Load data from follow up spreadsheet to DB'''
    cred = get_credentials_from_file()  # get_credentials func cannot run 
                                        # inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    folder_id = '0BxLCeg0VgIlYcEhodkxpTEpwTVE'
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = \
            ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    records = {}
    for f in files:
        file_name, file_id = f['name'], f['id']
        program_abbr, year = file_name.split('.')[0].split('_')
        program = AcademicProgram.query.filter_by(program_title_abbr=program_abbr.lower()).first()
        print(program.id, program_abbr)
        if FollowUpSummary.query.filter_by(survey_year=year).filter_by(program_id=program.id).first():
            print('Data of year {} already exists'.format(year))
            continue
        print('Loading data from file: {} {}'.format(file_name, file_id))
        try:
            wks = gc.open_by_key(file_id).sheet1
        except:
            print('Error!')
            continue
        else:
            col_no = 10  # employment status for MT
            if program.id == 2 and year == '2557':
                    col_no = 6  # employment status for RT
            empl_data = wks.col_values(col_no)[1:]
            employed = [e for e in empl_data if e.startswith(u'ได้งานทำ')
                            or e.startswith(u'ทำงาน')
                            or e.startswith(u'ศึกษาต่อ')
                            or e.startswith(u'ทำงานแล้ว')
                            or e.startswith(u'กำลังศึกษา')]  # what a hell

            empl_rate = len(employed) / float(len([d for d in empl_data if d != '']))
            print(program_abbr, year, empl_rate, len(employed))
            a = FollowUpSummary(program_id=program.id,
                    post_grad_employment_rate=empl_rate,survey_year=year)
            db.session.add(a)
            db.session.commit()
    return jsonify({'status': 'success'})


@education.route('/followup/results/')
@cross_origin()
def get_followup_result():
    query = db.session.query(FollowUpSummary.survey_year,
                                FollowUpSummary.post_grad_employment_rate,
                                AcademicProgram.program_title_abbr)
    query = query.join(AcademicProgram)
    results = query.all()
    d = []
    for r in results:
        d.append({
            'year': r[0],
            'rate': r[1],
            'program': r[2]
        })
    return jsonify(d)


@education.route('/gdrive/evaluation/update/')
def udpate_evaluation():
    '''Load data from evaluation spreadsheet to DB'''
    cred = get_credentials_from_file()  # get_credentials func cannot run 
                                        # inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    #folder_id = '0B45WRw4HPnk_bWhadnNxcDdQWm8'
    #folder_id = '0B22x_gLSu9r4Z3UzUXBhRHByLWs'
    folder_id = '0B45WRw4HPnk_dXBsOE9KTkpEVU0'
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = \
            ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    records = {}
    for f in files:
        file_name, file_id = f['name'], f['id']
        print(file_name.split('.'))
        program_abbr, year = file_name.split('.')[0].split('_')
        '''
        if FollowUpSummary.query.filter_by(survey_year=str(year)).first():
            print('Data of year {} already exists'.format(year))
            continue
        print('Loading data from file: {} {}'.format(file_name, file_id))
        '''
        wks = gc.open_by_key(file_id).sheet1
        empl_data = wks.col_values(8)[1:]
        print(empl_data)
        employed = [e for e in empl_data if e == u'ทำงาน' or e == u'ศึกษาต่อ']
        empl_rate = len(employed) / float(len(empl_data))
        if program_abbr == 'MT':
            program_id = 1
        elif program_abbr == 'RT':
            program_id = 2
        else:
            raise ValueError
        #a = FollowUpSummary(program_id=program_id,post_grad_employment_rate=empl_rate,survey_year=year)
        #db.session.add(a)
        #db.session.commit()
    return jsonify({'status': 'success'})