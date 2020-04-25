from flask import request, g, jsonify

from app.api import bp
from app.api.auth import token_auth
from app.projects.pointofcare_ocr.pointofcare_model import POC_OCR_Model


@bp.route('/pocresult', methods=['POST'])
@token_auth.login_required
def example_create():
    """Creates diagnosis from JSON data in the request."""
    print(request.headers)

    data = request.form.to_dict() or {}
    time = data.get('time')
    systolic = data.get('systolic')
    diastolic = data.get('diastolic')
    heartRate = data.get('heartRate')

    model = POC_OCR_Model(user_id=g.current_user.id, time=time, systolic=systolic, diastolic=diastolic,
                          heartRate=heartRate)
    model.save()

    return jsonify(model), 201


@bp.route('/poc')
@token_auth.login_required
def example_labels_get():
    print(request.headers)
    """Retrieves the possible labels which the data might be given."""
    return jsonify(POC_OCR_Model.possible_labels)
