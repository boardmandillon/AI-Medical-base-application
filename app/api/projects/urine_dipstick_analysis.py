from flask import request, g
from flask import jsonify

from app.api import bp
from app.api.auth import token_auth
from app.projects.urine_dipstick_analysis.urine_dipstick_model import \
    UrineDipstickModel
from app.api.errors import bad_request
from PIL import Image
import io
import base64
import binascii


@bp.route('/urine_dipstick_analysis/', methods=['POST'])
@token_auth.login_required
def create_urine_analysis():
    """Creates diagnosis from JSON data in the request.
    Decodes a base64 encoded image into binary form before sending
    to the project model. Verification of binary image data is done by
    PIL library.
    """
    data = request.get_json() or {}

    if not data.get('photo_base64'):
        return bad_request('must include content type and photo data in request')
    photo_base64 = data.get('photo_base64')

    try:
        diagnosis_photo = base64.b64decode(photo_base64, validate=True)
    except binascii.Error:
        return bad_request('failed to decode base64 string')
    del data['photo_base64']

    try:
        image = Image.open(io.BytesIO(diagnosis_photo))
        image.verify()
        content_type = image.format
        image.close()
    except IOError:
        return bad_request('image file is not valid')

    diagnosis = UrineDipstickModel(user_id=g.current_user.id, content_type=content_type,
                                   **data, diagnosis_photo=diagnosis_photo)
    diagnosis.save()

    return diagnosis.to_json(), 201


@bp.route('/urine_dipstick_analysis_images/')
@token_auth.login_required
def get_urine_analyses_image():
    """Retrieves analysis image corresponding to a given filename parameter
    for a specific user.
    """
    data = request.args.to_dict()

    if not data.get('filename'):
        return bad_request('must include filename')
    if not UrineDipstickModel.objects.filter(user_id=g.current_user.id,
                                             filename=data.get('filename')).first():
        return bad_request('no file with the name: ' + data.get('filename') + ' for this user')
    user_data = UrineDipstickModel.objects.filter(user_id=g.current_user.id,
                                                  filename=data.get('filename')).first()
    photo = user_data.diagnosis_photo.read()
    content_type = user_data.content_type

    # do what you want with image here, example writing image to given path
    extension = ''
    if content_type == 'image/jpeg':
        extension = '.jpg'
    out_filepath = '/Users/Miles/Desktop/test' + extension
    output = open(out_filepath, "wb")
    output.write(photo)
    output.close()
    data = {'message': 'image retrieved successfully'}
    return jsonify(data), 200


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
