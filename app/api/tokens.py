from flask import jsonify, g
from flask_jwt_extended import (
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)

from app import db_relational as db
from app.api import bp
from app.api.auth import basic_auth

@bp.route('/authenticate', methods=['POST'])
@basic_auth.login_required
def get_token():
    """Generates a token for a user and writes the token and expiration
    to the database
    """
    user_id = g.current_user.id
    email = g.current_user.email

    user = {"user" :{ "id" : user_id, "email" : email}}
    ret = {
        "access_token": create_access_token(identity=user),
        "refresh_token": create_refresh_token(identity=user),
        "user": {"id" : user_id, "email" : email}
    }

    return jsonify(ret), 200


@bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    user = get_jwt_identity()
    ret = {"access_token": create_access_token(identity=user)}

    return jsonify(ret), 200