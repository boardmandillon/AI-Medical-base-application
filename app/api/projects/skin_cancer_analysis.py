import base64
import binascii

from io import BytesIO
from PIL import Image
from flask import request, g, jsonify
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from app.api import bp
from app.api.errors import bad_request
from app.api.decorators import user_role_required
from app.models.user import UserRoles
from app.projects.skin_cancer_analysis.predictor import predictImage
from app.projects.skin_cancer_analysis.skin_cancer_model import skinCancerModel


@bp.route('/skin_cancer_analysis', methods=['POST'])
@jwt_required
def skin_cancer_create_diagnosis():
    """Extracts cancer image from JSON data in the request.

    Decodes a base64 encoded image into binary form before sending
    to the project model. The image is also saved locally to be
    used for prediction. Each time the method is called the
    image is saved with the same name, overwritting the previous image.

    Verification of binary image data is done by PIL library.
    """
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    if not data.get('photo_base64'):
        return bad_request('must include content type and photo data in request')
    photo_base64 = data.get('photo_base64')

    try:
        diagnosis_photo = base64.b64decode(photo_base64, validate=True)
    except binascii.Error:
        return bad_request('failed to decode base64 string')
    del data['photo_base64']

    try:
        imageBytes = BytesIO(diagnosis_photo)
        image = Image.open(imageBytes)

        image.save(r"app/projects/skin_cancer_analysis/image/data/image.jpg", "JPEG")

        content_type = image.format
        image.close()
    except IOError:
        return bad_request('image file is not valid')

    current_user = get_jwt_identity()

    diagnosis = skinCancerModel(user_id=current_user['id'], content_type=content_type,
                                **data, diagnosis_photo=diagnosis_photo)
    diagnosis.save()

    return jsonify(diagnosis), 201


@bp.route('/skin_cancer_analysis', methods=['GET'])
@jwt_required
def skin_cancer_get_diagnosis():
    """Called straight after skin_cancer_create_diagnosis().
    The predictor class is called and a prediction is output
    from the image saved previously and saved in the model.

    Once the prediction is received and saved, both the
    prediction and image are returned.

    """
    current_user = get_jwt_identity()

    try:
        prediction = predictImage()
        pred = skinCancerModel(user_id=current_user['id'], t_diagnosis=prediction)
        pred.save()
    except IOError:
        return bad_request('image file is not valid')

    with open(r"app/projects/skin_cancer_analysis/image/data/image.jpg", "rb") as image:
        f = image.read()
        b = bytearray(f)

    diagnosis_photo = base64.b64encode(b)
    response = {'prediction': prediction, 'image': diagnosis_photo.decode('utf-8')}

    return jsonify(response), 200


@bp.route('/records')
@jwt_required
def getRecords():
    """Retrieves all records relating to the user currently logged in."""
    current_user = get_jwt_identity()
    return jsonify(skinCancerModel.objects().filter(user_id=current_user['id']))


@bp.route('/skin_cancer_analysis/<doc_id>', methods=['DELETE'])
@jwt_required
def skin_cancer_diagnosis_delete_from_id(doc_id):
    """Deletes record corresponding to the given ID."""
    current_user = get_jwt_identity()
    skinCancerModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id']).delete()
    return jsonify({"success": True})


@bp.route('/skin_cancer_analysis/<doc_id>', methods=['PATCH'])
@jwt_required
@user_role_required(UserRoles.USER)
def skin_cancer_diagnosis_update(doc_id):
    """Updates fields of the document from the JSON data in the request."""
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    current_user = get_jwt_identity()

    model = skinCancerModel.objects.get_or_404(
        id=doc_id,
        user_id=current_user['id']
    )

    model.save(data)

    return jsonify(model)


@bp.route('/skin_cancer_analysis/labels')
@jwt_required
def skin_cancer_analysis_labels_get():
    """Retrieves the possible labels which the data might be given."""
    return jsonify(skinCancerModel.possible_labels)
