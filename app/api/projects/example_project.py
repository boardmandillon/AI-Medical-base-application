from flask import request, g, jsonify
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from app.api import bp
from app.projects.example_project.example_model import ExampleModel
from app.projects.example_project.example_project import ExampleProject
from app.api.decorators import user_role_required
from app.models.user import UserRoles


@bp.route('/example/', methods=['POST'])
@jwt_required()
def example_create():
    """Creates diagnosis from JSON data in the request."""
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    current_user = get_jwt_identity()
    return jsonify(ExampleProject.predict(data, current_user)), 201


@bp.route('/example/')
@jwt_required()
def example_get():
    """Retrieves a users documents."""
    current_user = get_jwt_identity()
    return jsonify(ExampleModel.objects().filter(user_id=current_user['id']))


@bp.route('/example/<doc_id>')
@jwt_required()
def example_get_from_id(doc_id):
    """Retrieves record corresponding to the given ID."""
    current_user = get_jwt_identity()

    example_doc = ExampleModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id'])

    return jsonify(example_doc)


@bp.route('/example/<doc_id>', methods=['DELETE'])
@jwt_required()
def example_delete_from_id(doc_id):
    """Deletes record corresponding to the given ID."""
    current_user = get_jwt_identity()

    ExampleModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id']).delete()
    return jsonify({"success": True})


@bp.route('/example/<doc_id>', methods=['PATCH'])
@jwt_required()
@user_role_required(UserRoles.USER)
def example_update(doc_id):
    """Updates fields of the document from the JSON data in the request."""
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    current_user = get_jwt_identity()

    model = ExampleModel.objects.get_or_404(
        id=doc_id, user_id=current_user['id'])
    model.save(data)

    return jsonify(model)


@bp.route('/example/labels')
@jwt_required()
def example_labels_get():
    """Retrieves the possible labels which the data might be given."""
    return jsonify(ExampleModel.possible_labels)
