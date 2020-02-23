from flask import request, g

from app.api import bp
from app.api.auth import token_auth
from app.models.projects.example_model import ExampleModel
from app.machine_learning.example_project.example_project import ExampleProject


@bp.route('/example/', methods=['POST'])
@token_auth.login_required
def example_create():
    """Creates diagnosis from JSON data in the request."""
    data = request.form.to_dict() or {}
    example_project = ExampleProject()

    return example_project.predict(data, g.current_user).to_json()


@bp.route('/example/<doc_id>')
@token_auth.login_required
def example_get_from_id(doc_id):
    """Retrieves record corresponding to the given ID."""
    return ExampleModel.objects().filter(id=doc_id).to_json()
