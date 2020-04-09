from flask import request, g

from app.api import bp
from app.api.auth import token_auth
from app.projects.urine_dipstick_analysis.urine_dipstick_model import \
    UrineDipstickModel
from app.api.errors import bad_request
import base64
import binascii


@bp.route('/urine_dipstick_analysis/', methods=['POST'])
@token_auth.login_required
def create_urine_analysis():
    """Creates diagnosis from JSON data in the request.
    Decodes a base64 encoded image into binary form before sending
    to the project model. It is expected that the mime type will be
    provided by the client in order to identify the file extension type.
    Each file uploaded by a user will need a unique file name for identification.
    """
    data = request.get_json() or {}

    if not data.get('filename') or not data.get('content_type') \
            or not data.get('photo_base64'):
        return bad_request('must include filename, content type and photo data in request')
    elif UrineDipstickModel.objects.filter(user_id=g.current_user.id,
                                           filename=data.get('filename')).first():
        return bad_request('please use a different filename for this user')
    photo_base64 = data.get('photo_base64')
    try:
        diagnosis_photo = base64.b64decode(photo_base64, validate=True)
    except binascii.Error:
        return bad_request('failed to decode base64 string')
    del data['photo_base64']

    diagnosis = UrineDipstickModel(user_id=g.current_user.id, **data,
                                   diagnosis_photo=diagnosis_photo)
    diagnosis.save()

    return diagnosis.to_json()


@bp.route('/urine_dipstick_analysis/')
@token_auth.login_required
def get_urine_analyses():
    """Retrieves analysis corresponding to the given query parameters.

    For example using the following query will return the analysis results of
    the user with an id of 1:
        <base URL>/urine_dipstick_analysis?user_id=1
    """
    query_params = request.args.to_dict()
    return UrineDipstickModel.objects().filter(**query_params).to_json()
