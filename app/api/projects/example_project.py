from flask import request, g, jsonify

from app.api import bp
from app.api.auth import token_auth
from app.projects.example_project.example_model import ExampleModel
from app.projects.example_project.example_project import ExampleProject
from app.api.decorators import user_role_required
from app.models.user import UserRoles


@bp.route('/example/', methods=['POST'])
@token_auth.login_required
def example_create():
    """Creates diagnosis from JSON data in the request."""
    data = request.form.to_dict() or {}
    return jsonify(
        ExampleProject.predict(data, g.current_user)), 201


@bp.route('/example/')
@token_auth.login_required
def example_get():
    """Retrieves a users documents."""
    return jsonify(ExampleModel.objects().filter(
        user_id=g.current_user.id))


@bp.route('/example/<doc_id>')
@token_auth.login_required
def example_get_from_id(doc_id):
    """Retrieves record corresponding to the given ID."""
    example_doc = ExampleModel.objects.get_or_404(
        id=doc_id, user_id=g.current_user.id)
    return jsonify(example_doc)


@bp.route('/example/<doc_id>', methods=['PATCH'])
@token_auth.login_required
@user_role_required(UserRoles.USER)
def example_update(doc_id):
    """Updates fields of the document from the JSON data in the request."""
    data = request.form.to_dict() or {}

    model = ExampleModel.objects.get_or_404(
        id=doc_id, user_id=g.current_user.id)
    model.save(data)

    return jsonify(model)


@bp.route('/example/labels')
@token_auth.login_required
def example_labels_get():
    """Retrieves the possible labels which the data might be given."""
    return jsonify(ExampleModel.possible_labels)
