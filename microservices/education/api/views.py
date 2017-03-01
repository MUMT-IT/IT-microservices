import gspread
import httplib2

from flask import jsonify, request, redirect, session
from . import education_bp as education
from .drive import get_file_list, get_credentials_from_file
from apiclient import discovery
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials


@education.route('/followUp/update/')
def followup():
    '''Load data from Spreadsheet to DB'''
    cred = get_credentials_from_file()  # get_credentials func cannot run inside flask this way
    http = cred.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    folder_id = '0BxLCeg0VgIlYcEhodkxpTEpwTVE'
    files = get_file_list(folder_id, cred)
    service_key_file = 'api/AcademicAffairs-420cd46d6400.json'
    scope = ['https://spreadsheets.google.com/feeds']
    gc_credentials = ServiceAccountCredentials.from_json_keyfile_name(service_key_file, scope)
    gc = gspread.authorize(gc_credentials)
    for f in files:
        file_name, file_id = f['name'], f['id']
        try:
            wks = gc.open_by_key(file_id).sheet1
        except:
            batch = service.new_batch_http_request()
            user_permission = {
                'type': 'user',
                'role': 'reader',
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
            row = 1
            headings = wks.row_values(row)
            print(headings)
        break
    return 200