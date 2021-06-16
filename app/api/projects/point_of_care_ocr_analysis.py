import flask
import werkzeug
from flask import request , jsonify
from flask_jwt_extended import (jwt_required , get_jwt_identity)
from app.api import bp
from app.api.errors import bad_request
from app.projects.pointofcare_ocr.pointofcare import PointOfCareOCR
from app.projects.pointofcare_ocr.pointofcare_model import POC_OCR_Model
from flask import current_app as app

from app.projects.pointofcare_ocr.predictor import predict


@bp.route ( '/pocimg' , methods=['POST'] )
@jwt_required()
def pocpic():
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}
    app.logger.info (
        "Data receive: {}".format(data))
    if not flask.request.files['monitor_image']:
        app.logger.info("must include content type and photo data in request")
        return bad_request('must include content type and photo data in request')
    monitor_image = flask.request.files['monitor_image']
    monitor_type = data.get('monitor_type')
    app.logger.info("Monitor type: {}".format(monitor_type))
    app.logger.info("Image: {}".format(monitor_image))
    filename = werkzeug.utils.secure_filename(monitor_image.filename)
    monitor_image.save(filename)
    if monitor_type == "Omron RS4":
        results = predict("omron_rs4", filename)
    elif monitor_type == "A&D UA-611":
        results = predict("a&d", filename)
    else:
        results = predict("kinetik", filename)

    ret = {
        "systolic": results[0],
        "diastolic": results[1],
        "pulse": results[2],
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
    current_user = get_jwt_identity()
    model = PointOfCareOCR._save_data(data, current_user)
    app.logger.info("Model saved: {}".format(model))
    return jsonify(model), 201


@bp.route ( '/getpocresult' )
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
