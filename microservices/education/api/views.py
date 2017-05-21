# -*- coding:utf8 -*-
import gspread
import httplib2
import numpy as np

from collections import defaultdict

from flask import jsonify
from . import education_bp as education
from .drive import get_file_list, get_credentials_from_file
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from flask_cors import cross_origin
from main import db
from models import (SurveyCategory, SurveyWRSSummary,
                    SurveyWRSTeachingSummary, FollowUpSummary,
                    AcademicProgram, EvaluationSummary,
                    WRSEdpexScore, WRSEdpexTopic)


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
            post_knowledge = [int(d) for d in post_knowledge[:i]]
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
            col_no = 10  # employment status for MT from 2558 onwards
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

    folder_id = '0B45WRw4HPnk_bWhadnNxcDdQWm8'  # evaluation folder
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = \
            ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    records = {}
    for f in files:
        print(f['name'])
        file_name, file_id = f['name'], f['id']
        try:
            program_abbr, year = file_name.split('.')[0].split('_')
        except:
            print('Invalid filename. Skipped.')
            continue
        print('Loading data from file: {} {}'.format(file_name, file_id))
        program = AcademicProgram.query.filter_by(program_title_abbr=program_abbr.lower())\
                                        .filter_by(level='undergraduate').first()
        e = EvaluationSummary.query.filter_by(survey_year=year)\
                                        .filter_by(program_id=program.id).first()
        if e:
            print('Data of the year {} already exists.'.format(year))
            continue
        try:
            wks = gc.open_by_key(file_id).sheet1
        except:
            print('Error!')
            continue
        else:
            morals = []
            for i in range(22,29):
                morals.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_morals_list = []
            for i in range(len(morals)):
                avg = np.mean(morals[i])
                avg_morals_list.append(avg)
            avg_morals = np.mean(avg_morals_list)

            knowledge = []
            for i in range(29, 36):
                knowledge.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_knowledge_list = []
            for i in range(len(knowledge)):
                avg = np.mean(knowledge[i])
                avg_knowledge_list.append(avg)
            avg_knowledge = np.mean(avg_knowledge_list)

            thinking = []
            for i in range(36, 40):
                thinking.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_thinking_list = []
            for i in range(len(thinking)):
                avg = np.mean(thinking[i])
                avg_thinking_list.append(avg)
            avg_thinking = np.mean(avg_thinking_list)

            relation = []
            for i in range(40, 47):
                relation.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_relation_list = []
            for i in range(len(relation)):
                avg = np.mean(relation[i])
                avg_relation_list.append(avg)
            avg_relation = np.mean(avg_relation_list)

            analytics = []
            for i in range(47, 52):
                analytics.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_analytics_list = []
            for i in range(len(analytics)):
                avg = np.mean(analytics[i])
                avg_analytics_list.append(avg)
            avg_analytics = np.mean(avg_analytics_list)

            professional = []
            for i in range(52, 55):
                professional.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_professional_list = []
            for i in range(len(professional)):
                avg = np.mean(professional[i])
                avg_professional_list.append(avg)
            avg_professional = np.mean(avg_professional_list)

            identity = []
            for i in range(55, 58):
                identity.append([int(d) for d in wks.col_values(i)[1:] if d != ''])
            avg_identity_list = []
            for i in range(len(identity)):
                avg = np.mean(identity[i])
                avg_identity_list.append(avg)
            avg_identity = np.mean(avg_identity_list)

            overall = [int(d) for d in wks.col_values(58)[1:] if d != '']
            avg_overall = np.mean(overall)

            a = EvaluationSummary(survey_year=year,
                                    avg_morals=avg_morals,
                                    avg_thinking=avg_thinking,
                                    avg_relation=avg_relation,
                                    avg_professional=avg_professional,
                                    avg_analytics=avg_analytics,
                                    avg_identity=avg_identity,
                                    avg_knowledge=avg_knowledge,
                                    avg_overall=avg_overall,
                                    program_id=program.id)
            db.session.add(a)
            db.session.commit()
    return jsonify({'status': 'success'})


@education.route('/evaluation/results/')
@cross_origin()
def get_evaluation_result():
    query = db.session.query(EvaluationSummary.survey_year,
                                EvaluationSummary.avg_analytics,
                                EvaluationSummary.avg_identity,
                                EvaluationSummary.avg_knowledge,
                                EvaluationSummary.avg_morals,
                                EvaluationSummary.avg_professional,
                                EvaluationSummary.avg_relation,
                                EvaluationSummary.avg_thinking,
                                EvaluationSummary.avg_overall,
                                AcademicProgram.level,
                                AcademicProgram.program_title_abbr,
                                )
    query = query.join(AcademicProgram)
    results = query.all()
    d = []
    for res in results:
        r = {'year': res[0],
                'program': res[-1].upper(),
                'level': res[-2],
                'avg_analytics': res[1],
                'avg_identity': res[2],
                'avg_knowledge': res[3],
                'avg_morals': res[4],
                'avg_professional': res[5],
                'avg_relation': res[6],
                'avg_thinking': res[7],
                'avg_overall': res[8]
        }
        d.append(r)
    return jsonify(d)


@education.route('/evaluation/edpex/wrs/load/')
@cross_origin()
def load_edpex_wrs_results():
    cred = get_credentials_from_file()  # get_credentials func cannot run
    # inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    folder_id = '0B45WRw4HPnk_YlhxbjFJeDVoWk0'
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = \
        ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    for f in files:
        file_name, file_id = f['name'], f['id']
        print('Loading data from file: {} {}'.format(file_name, file_id))
        try:
            wks = gc.open_by_key(file_id).get_worksheet(4)
        except:
            print('Error!')
            continue
        else:
            t_professional = WRSEdpexTopic.objects(slug="professional").first()
            t_creativity = WRSEdpexTopic.objects(slug="creativity").first()
            t_analytical = WRSEdpexTopic.objects(slug="analytical").first()
            t_leadership = WRSEdpexTopic.objects(slug="leadership").first()
            t_social_resp = WRSEdpexTopic.objects(slug="social_resp").first()
            for idx in range(2,6):
                year = int(wks.col_values(idx)[2].split()[-1])
                scores = wks.col_values(idx)[3:8]
                professional_score = WRSEdpexScore(score=float(scores[0]), year=year)
                creativity_score = WRSEdpexScore(score=scores[1], year=year)
                analytical_score = WRSEdpexScore(score=scores[2], year=year)
                leadership_score = WRSEdpexScore(score=scores[3], year=year)
                social_score = WRSEdpexScore(score=scores[4], year=year)
                t_professional.scores.append(professional_score)
                t_creativity.scores.append(creativity_score)
                t_analytical.scores.append(analytical_score)
                t_leadership.scores.append(leadership_score)
                t_social_resp.scores.append(social_score)
                t_professional.save()
                t_creativity.save()
                t_leadership.save()
                t_analytical.save()
                t_social_resp.save()
    return jsonify([])


@education.route('/evaluation/edpex/wrs/')
@cross_origin()
def get_edpex_wrs_results():
    data = []
    for slug in ["professional", "creativity", "analytical",
                 "leadership", "social_resp"]:
        t = WRSEdpexTopic.objects(slug=slug).first()
        scores = [dict(year=s.year, score=s.score) for s in t.scores]
        data.append(dict(slug=slug, scores=scores, desc=t.desc))
    return jsonify(data)
