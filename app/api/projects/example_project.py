from flask import request, g

import json

from app.api import bp
from app.api.auth import token_auth
from app.models.projects.example_model import ExampleModel
from app.machine_learning.example_project.example_project import ExampleProject


@bp.route('/example/', methods=['POST'])
@token_auth.login_required
def example_create():
    """Creates diagnosis from JSON data in the request."""
    data = request.form.to_dict() or {}
    return ExampleProject.predict(data, g.current_user).to_json()


@bp.route('/example/')
@token_auth.login_required
def example_get():
    """Retrieves results corresponding to the given query parameters.

    For example using the following query will return the results of the
    user with an id of 1:
        <base URL>/example?user_id=1
    """
    query_params = request.args.to_dict()
    return ExampleModel.objects().filter(**query_params).to_json()


@bp.route('/example/<doc_id>')
@token_auth.login_required
def example_get_from_id(doc_id):
    """Retrieves record corresponding to the given ID."""
    return ExampleModel.objects().filter(id=doc_id).to_json()


@bp.route('/example/<doc_id>', methods=['PATCH'])
@token_auth.login_required
def example_update(doc_id):
    """Updates fields of the document from the JSON data in the request."""
    data = request.form.to_dict() or {}

    model = ExampleModel.objects(id=doc_id).get()
    model.save(data)

    return model.to_json()


@bp.route('/example/labels')
@token_auth.login_required
def example_labels_get():
    """Retrieves the possible labels which the data might be given."""
    return json.dumps(ExampleProject.get_possible_labels())
