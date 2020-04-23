from flask import request, g, jsonify
from app.api import bp
from app.api.auth import token_auth
from app.projects.skin_cancer_analysis.predictor import predictImage
from app.projects.skin_cancer_analysis.skin_cancer_model import skinCancerModel
from app.api.errors import bad_request
from PIL import Image

import io
import base64
import binascii
import bson


@bp.route('/skin_cancer_analysis/', methods=['POST'])
@token_auth.login_required
def upload_cancer_analysis_image():
    """Extracts cancer image from JSON data in the request.

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

    diagnosis = skinCancerModel(user_id=g.current_user.id, content_type=content_type,
                                **data, diagnosis_photo=diagnosis_photo)
    diagnosis.save()

    return diagnosis.to_json(), 201


@bp.route('/skin_cancer_analysis/', methods=['GET'])
@token_auth.login_required
def get_cancer_analysis():
    """Retrieves analysis image corresponding to a given document object ID
    passed as a URL parameter.

    For example <base URL>/urine_dipstick_analysis_images?id=<object ID here>
    """
    data = request.args.to_dict()

    if not data.get('id'):
        return bad_request('must include image file id')
    object_id = data.get('id')

    if not skinCancerModel.objects.get(
            user_id=g.current_user.id,
            diagnosis_photo=bson.objectid.ObjectId(object_id)):
        return bad_request('no file with the id: ' + data.get('id') + ' for this user')

    user_data = skinCancerModel.objects.get(
        user_id=g.current_user.id, diagnosis_photo=bson.objectid.ObjectId(object_id))
    diagnosis_photo = user_data.diagnosis_photo.read()
    #content_type = user_data.content_type

    diagnosis_photo.save(r"image/data/image.jpg")
    prediction = predictImage()

    data = {'message': 'image retrieved successfully'}
    return jsonify(prediction=prediction), 200
