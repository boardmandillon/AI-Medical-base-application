from flask import request, g

from app.api import bp
from app.api.auth import token_auth
from app.models.projects.example_model import ExampleModel
from app.machine_learning.example_project.example_project import ExampleProject

# An example to use when defining your own projects
exampleProject = ExampleProject()


@bp.route('/example/', methods=['POST'])
@token_auth.login_required
def example_create():
    """Creates diagnosis from JSON data in the request."""
    data = request.form.to_dict() or {}

    return exampleProject.predict(data, g.current_user).to_json()


@bp.route('/example/')
@token_auth.login_required
def example_get():
    """Retrieves record corresponding to the given query parameters.

    For example using the following query will return the diagnoses of the
    document with an id of 5e4ea02d4ed54e1e14bc6783:
        <base URL>/example?id=5e4ea02d4ed54e1e14bc6783
    """
    query_params = request.args.to_dict()
    return ExampleModel.objects().filter(**query_params).to_json()
