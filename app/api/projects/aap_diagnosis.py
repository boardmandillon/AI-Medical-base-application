from flask import request, g, jsonify
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import datetime

from app.api import bp
from app.api.decorators import user_role_required
from app.api.errors import bad_request
from app.models.user import UserRoles
from app.projects.aap_diagnosis.aap_diagnosis_model import AAPDiagnosisModel
from app.projects.aap_diagnosis.aap_diagnosis import AAPDiagnosis


@bp.route('/aap-diagnosis/', methods=['POST'])
@jwt_required
def aap_create_diagnosis():
    """Creates diagnosis from JSON data in the request."""
    if 'application/json' in request.headers['Content-Type']:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    current_user = get_jwt_identity()

    model, error = AAPDiagnosis.predict(data, current_user)
    if model and not error:
        return jsonify(model), 201
    else:
        return bad_request(error)


@bp.route('/aap-diagnosis/')
@jwt_required
def aap_get_diagnoses():
    """Retrieves diagnoses of a user."""
    current_user = get_jwt_identity()
    return jsonify(AAPDiagnosisModel.objects().filter(user_id=current_user['id']))


@bp.route('/aap-diagnosis/<doc_id>')
@jwt_required
def aap_get_diagnosis_from_id(doc_id):
    """Retrieves diagnosis corresponding to the given ID."""
    current_user = get_jwt_identity()

    model = AAPDiagnosisModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id'])
    return jsonify(model.to_dict())


@bp.route('/aap-diagnosis/<doc_id>', methods=['DELETE'])
@jwt_required
def aap_delete_diagnosis_from_id(doc_id):
    """Deletes diagnosis corresponding to the given ID."""
    current_user = get_jwt_identity()

    AAPDiagnosisModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id']).delete()
    return jsonify({"success": True})


@bp.route('/aap-diagnosis/<doc_id>', methods=['PATCH'])
@jwt_required
@user_role_required(UserRoles.EXPERT)
def confirm_aap_diagnosis(doc_id):
    """Updates actual diagnosis field of the given record."""
    if 'application/json' in request.headers['Content-Type']:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    current_user = get_jwt_identity()

    model = AAPDiagnosisModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id'])

    if not model.set_actual_diagnosis(data.get("l_actual_diagnosis")):
        return bad_request(
            "Please confirm one of the following diseases: {}".format(
                list(model.possible_labels.keys())))
    else:
        model.date_modified = datetime.datetime.utcnow()
        model.save()
        return jsonify(model.to_dict())


@bp.route('/aap-diagnosis/dataset-accuracy')
@jwt_required
def aap_get_dataset_accuracy():
    """Retrieves dataset accuracy."""
    score = AAPDiagnosis.model_accuracy()
    if score:
        return jsonify(score), 201
    else:
        return bad_request("Error calculating accuracy.")