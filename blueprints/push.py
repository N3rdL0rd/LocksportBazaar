from flask import Blueprint, jsonify, send_from_directory

from common.user_util import get_unpushed

push_blueprint = Blueprint('push_blueprint', __name__,
                        template_folder='templates')

@push_blueprint.route('/push/<token>')
def get_push(token):
    return jsonify(get_unpushed(token))

@push_blueprint.route('/push_sw.js')
def sw():
    return send_from_directory("static", "notif_sw.js")