from flask import request, g, jsonify
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import datetime

from app.api import bp
from app.api.decorators import user_role_required
from app.api.errors import bad_request
from app.models.user import UserRoles
from app.projects.aap_diagnosis.aap_diagnosis_model import AAPDiagnosisModel, AAPMenDiagnosisModel, AAPWomenDiagnosisModel
from app.projects.aap_diagnosis.aap_diagnosis import AAPDiagnosis
from app.projects.aap_diagnosis.aap_men_diagnosis import AAPMenDiagnosis
from app.projects.aap_diagnosis.aap_women_diagnosis import AAPWomenDiagnosis


@bp.route('/aap-diagnosis/', methods=['POST'])
@jwt_required()
def aap_create_diagnosis():
    """Creates diagnosis from JSON data in the request."""
    if 'application/json' in request.headers['Content-Type']:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    current_user = get_jwt_identity()

    model, error = AAPDiagnosis.predict(data, current_user)

    # create diagnosis from other classifiers too
    men_model, men_error = AAPMenDiagnosis.predict(data, current_user, model.id)
    women_model, women_error = AAPWomenDiagnosis.predict(data, current_user, model.id)

    if model and not error and not men_error and not women_error:
        return jsonify(model), 201
    else:
        return bad_request(error, men_error, women_error)


@bp.route('/aap-diagnosis/')
@jwt_required()
def aap_get_diagnoses():
    """Retrieves AAP diagnoses of a user (main dataset)."""
    current_user = get_jwt_identity()
    return jsonify(AAPDiagnosisModel.objects().filter(user_id=current_user['id']))


@bp.route('/aap-diagnosis/<doc_id>')
@jwt_required()
def aap_get_diagnosis_from_id(doc_id):
    """Retrieves diagnosis corresponding to the given ID."""
    current_user = get_jwt_identity()

    model = AAPDiagnosisModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id'])
    return jsonify(model.to_dict())

@bp.route('/aap-men-diagnosis/<doc_id>')
@jwt_required()
def aap_men_get_diagnosis_from_id(doc_id):
    """Retrieves men diagnosis corresponding to the given AAP ID."""
    current_user = get_jwt_identity()

    model = AAPMenDiagnosisModel.objects.get_or_404(
        aap_id=doc_id, user_id=current_user['id'])
    return jsonify(model.to_dict())

@bp.route('/aap-women-diagnosis/<doc_id>')
@jwt_required()
def aap_women_get_diagnosis_from_id(doc_id):
    """Retrieves women diagnosis corresponding to the given AAP ID."""
    current_user = get_jwt_identity()
    
    model = AAPWomenDiagnosisModel.objects.get_or_404(
        aap_id=doc_id, user_id=current_user['id'])
    return jsonify(model.to_dict())


@bp.route('/aap-diagnosis/<doc_id>', methods=['DELETE'])
@jwt_required()
def aap_delete_diagnosis_from_id(doc_id):
    """Deletes diagnoses corresponding to the given ID,
         across all AAPDiagnosis datasets."""
    current_user = get_jwt_identity()

    AAPDiagnosisModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id']).delete()
    
    AAPMenDiagnosisModel.objects.get_or_404(
        aap_id=doc_id, user_id=current_user['id']).delete()
    
    AAPWomenDiagnosisModel.objects.get_or_404(
        aap_id=doc_id, user_id=current_user['id']).delete()

    
    return jsonify({"success": True})


@bp.route('/aap-diagnosis/<doc_id>', methods=['PATCH'])
@jwt_required()
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
@jwt_required()
def aap_get_dataset_accuracy():
    """Retrieves aap dataset accuracy."""
    score = AAPDiagnosis.model_accuracy()
    if score:
        return jsonify(score), 201
    else:
        return bad_request("Error calculating accuracy.")

@bp.route('/aap-men-diagnosis/dataset-accuracy')
@jwt_required()
def aap_men_get_dataset_accuracy():
    """Retrieves men dataset accuracy."""
    score = AAPMenDiagnosis.model_accuracy()
    if score:
        return jsonify(score), 201
    else:
        return bad_request("Error calculating accuracy.")

@bp.route('/aap-women-diagnosis/dataset-accuracy')
@jwt_required()
def aap_women_get_dataset_accuracy():
    """Retrieves women dataset accuracy."""
    score = AAPWomenDiagnosis.model_accuracy()
    if score:
        return jsonify(score), 201
    else:
        return bad_request("Error calculating accuracy.")