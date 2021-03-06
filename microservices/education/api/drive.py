#from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'api/client_secret.json'
APPLICATION_NAME = 'MUMT-IT'

def get_credentials():
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'drive-python-readonly.json')
    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to' + credential_path)
    return credentials


def get_credentials_from_file():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'drive-python-readonly.json')
    store = Storage(credential_path)
    credentials = store.get()
    return credentials


def get_file_list(folder_id, credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    results = service.files().list(
        pageSize=10,
        q="'%s' in parents" % str(folder_id),
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        return []
    else:
        files = []
        for item in items:
            files.append({'id': item['id'], 'name': item['name']})
            #print('{0} ({1})'.format(item['name'], item['id']))
        return files

if __name__=='__main__':
    credentials = get_credentials()
    print(credentials.to_json())