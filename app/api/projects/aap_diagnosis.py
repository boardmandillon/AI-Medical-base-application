from flask import request, g

from app.api import bp
from app.api.auth import token_auth
from app.projects.aap_diagnosis.aap_diagnosis import AAPDiagnosis


@bp.route('/aap_diagnosis/', methods=['POST'])
@token_auth.login_required
def aap_create_diagnosis():
    """Creates diagnosis from JSON data in the request."""
    data = request.get_json() or {}

    diagnosis = AAPDiagnosis(user_id=g.current_user.id, **data)
    diagnosis.save()

    return diagnosis.to_json()


@bp.route('/aap_diagnosis/')
@token_auth.login_required
def aap_get_diagnoses():
    """Retrieves diagnoses corresponding to the given query parameters.

    For example using the following query will return the diagnoses of the
    user with an id of 1:
        <base URL>/aap_diagnosis?user_id=1
    """
    query_params = request.args.to_dict()
    return AAPDiagnosis.objects().filter(**query_params).to_json()
