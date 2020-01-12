from flask import request, g

from app.api import bp
from app.api.auth import token_auth
from app.models.projects.urine_dipstick_analysis import UrineDipstickAnalysis


@bp.route('/urine_dipstick_analysis/', methods=['POST'])
@token_auth.login_required
def create_urine_analysis():
    """Creates diagnosis from JSON data in the request."""
    data = request.get_json() or {}

    diagnosis = UrineDipstickAnalysis(user_id=g.current_user.id, **data)
    diagnosis.save()

    return diagnosis.to_json()


@bp.route('/urine_dipstick_analysis/')
@token_auth.login_required
def get_urine_analyses():
    """Retrieves analysis corresponding to the given query parameters.

    For example using the following query will return the analysis results of
    the user with an id of 1:
        <base URL>/urine_dipstick_analysis?user_id=1
    """
    query_params = request.args.to_dict()
    return UrineDipstickAnalysis.objects().filter(**query_params).to_json()
