from flask import jsonify, request
from . import education_bp as education
from .drive import get_file_list

@education.route('/followup/')
def followup():
    folder_id = '0BxLCeg0VgIlYcEhodkxpTEpwTVE'
    return jsonify(get_file_list(folder_id))