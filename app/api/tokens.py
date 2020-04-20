from flask import jsonify, g

from app import db_relational as db
from app.api import bp
from app.api.auth import basic_auth
from app.api.auth import token_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """Generates a token for a user and writes the token and expiration
    to the database
    """
    token = g.current_user.get_token()
    db.session.commit()
    user_id = g.current_user.id
    email = g.current_user.email
    return jsonify({'token': token,"user" :{ "id" : user_id, "email" : email}})


@bp.route('tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """Client can invalidate a token by sending a delete request
    """
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
