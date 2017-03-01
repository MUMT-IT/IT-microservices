from flask import jsonify, request
from utils.drive import get_file_list
from . import education_bp as education

@education.route('/followup/')
def followup():
    folder_id = '0BxLCeg0VgIlYcEhodkxpTEpwTVE'
    return jsonify(get_file_list(folder_id))