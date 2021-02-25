from flask import request, g, jsonify
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from app.api import bp
from app.projects.urine_dipstick_analysis.urine_dipstick_model import \
    UrineDipstickModel
from app.projects.urine_dipstick_analysis.urine_dipstick_image_pre_processing import \
    image_pre_processing
from app.projects.urine_dipstick_analysis.urine_dipstick_colour_detection import \
    squares_colour_detection
from app.api.errors import bad_request
from PIL import Image
import io
import base64
import binascii
import bson


@bp.route('/urine_dipstick_analysis/', methods=['POST'])
@jwt_required
def upload_urine_analysis_image():
    """Extracts urine dipstick image from JSON data in the request.

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

    current_user = get_jwt_identity()

    diagnosis = UrineDipstickModel(user_id=current_user['id'], content_type=content_type,
                                   **data, diagnosis_photo=diagnosis_photo)
    diagnosis.save()

    return diagnosis.to_json(), 201


@bp.route('/urine_dipstick_analysis/', methods=['GET'])
@jwt_required
def get_urine_analysis():
    """Retrieves analysis image corresponding to a given document object ID
    passed as a URL parameter.

    For example <base URL>/urine_dipstick_analysis_images?id=<object ID here>
    """
    data = request.args.to_dict()
    current_user = get_jwt_identity()

    if not data.get('id'):
        return bad_request('must include image file id')
    object_id = data.get('id')

    if not UrineDipstickModel.objects.get(
            user_id=current_user['id'],
            diagnosis_photo=bson.objectid.ObjectId(object_id)):
        return bad_request('no file with the id: ' + data.get('id') + ' for this user')

    user_data = UrineDipstickModel.objects.get(
        user_id=current_user['id'], diagnosis_photo=bson.objectid.ObjectId(object_id))
    diagnosis_photo = user_data.diagnosis_photo.read()

    results = image_pre_processing(diagnosis_photo)
    dipstick_squares = None
    if not results[0]:
        return bad_request(results[1])
    elif results[0]:
        dipstick_squares = results[1]

    diagnosis_results = squares_colour_detection(dipstick_squares)

    data = diagnosis_results
    return jsonify(data), 200
