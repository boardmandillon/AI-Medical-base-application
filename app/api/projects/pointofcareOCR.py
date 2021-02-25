from flask import request, g, jsonify
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from app.api import bp
from app.projects.pointofcare_ocr.pointofcare_model import POC_OCR_Model


@bp.route('/pocresult', methods=['POST'])
@jwt_required
def pocResult():
    """Creates record of Blood pressure results from JSON data in the request."""
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    time = data.get('time')
    systolic = data.get('systolic')
    diastolic = data.get('diastolic')
    heartRate = data.get('heartRate')

    current_user = get_jwt_identity()

    model = POC_OCR_Model(
        user_id=current_user['id'],
        time=time,
        systolic=systolic,
        diastolic=diastolic,
        heartRate=heartRate
    )

    model.save()
    return jsonify(model), 201


@bp.route('/pocresult')
@jwt_required
def getPocRecords():
    """Retrieves records of a user."""
    current_user = get_jwt_identity()
    return jsonify(POC_OCR_Model.objects().filter(user_id=current_user['id']))


@bp.route('/pocresult/<doc_id>', methods=['DELETE'])
@jwt_required
def poc_delete_from_id(doc_id):
    """Deletes records corresponding to the given ID."""
    current_user = get_jwt_identity()
    POC_OCR_Model.objects.get_or_404(id=doc_id, user_id=current_user['id']).delete()

    return jsonify({"success": True})
