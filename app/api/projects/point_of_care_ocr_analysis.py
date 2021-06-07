import base64
import binascii
from io import BytesIO

from PIL.Image import Image
from flask import request , jsonify
from flask_jwt_extended import (jwt_required , get_jwt_identity)
from app.api import bp
from app.api.errors import bad_request
from app.projects.pointofcare_ocr.pointofcare import PointOfCareOCR
from app.projects.pointofcare_ocr.pointofcare_model import POC_OCR_Model
from flask import current_app as app


@bp.route ( '/pocimg' , methods=['POST'] )
@jwt_required()
def pocpic():
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}
    # app.logger.info (
    #     "{} Data receive: {}".format (
    #         PointOfCareOCR.PROJECT_NAME , data ) )
    if not data.get('monitor_image'):
        app.logger.info("must include content type and photo data in request")
        return bad_request('must include content type and photo data in request')
    photo_base64 = data.get('monitor_image')

    # app.logger.info("Image base64 string {}".format(photo_base64))
    # try:
    #     app.logger.info("decode base64 string")
    #     diagnosis_photo = base64.b64decode(photo_base64, validate=True)
    # except binascii.Error:
    #     app.logger.info("failed to decode base64 string")
    #     return bad_request('failed to decode base64 string')
    # del data['monitor_image']
    #
    # try:
    #     imageBytes = BytesIO(diagnosis_photo)
    #     image = Image.open(imageBytes)
    #
    #     content_type = image.format
    #     image.close()
    # except IOError:
    #     return bad_request('image file is not valid')

    current_user = get_jwt_identity()
    #TODO: insert predicting algorithm function here
    ret = {
        "systolic": "0",
        "diastolic": "0",
        "pulse": "0",
        "time": "0"
    }
    return jsonify(ret), 200


@bp.route ( '/pocresult' , methods=['POST'] )
@jwt_required()
def pocResult():
    """Creates record of Blood pressure results from JSON data in the request."""
    if request.headers['Content-Type'] == 'application/json' :
        data = request.get_json () or {}
    else :
        data = request.form.to_dict () or {}

    app.logger.info("Data receive: {}".format(data))
    # time = data.get('time')
    # systolic = data.get('systolic')
    # diastolic = data.get('diastolic')
    # pulse = data.get('heartRate')

    current_user = get_jwt_identity()
    model = PointOfCareOCR._save_data(data, current_user)
    app.logger.info("Model saved: {}".format(model))
    # model = POC_OCR_Model(
    #     user_id=current_user['id'] ,
    #     time=time ,
    #     systolic=systolic ,
    #     diastolic=diastolic ,
    #     heartRate=pulse
    # )
    #
    # model.save()
    return jsonify(model), 201


@bp.route ( '/pocresult' )
@jwt_required()
def getPocRecords () :
    """Retrieves records of a user."""
    current_user = get_jwt_identity ()
    return jsonify ( POC_OCR_Model.objects ().filter ( user_id=current_user['id'] ) )


@bp.route ( '/pocresult/<doc_id>' , methods=['DELETE'] )
@jwt_required()
def poc_delete_from_id ( doc_id ) :
    """Deletes records corresponding to the given ID."""
    current_user = get_jwt_identity ()
    POC_OCR_Model.objects.get_or_404 ( id=doc_id , user_id=current_user['id'] ).delete ()

    return jsonify ( {"success" : True})
