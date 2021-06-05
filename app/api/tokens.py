import redis
from flask import jsonify , g
from flask import current_app as app
from flask import request
from flask_jwt_extended import (
    jwt_refresh_token_required ,
    create_access_token ,
    create_refresh_token ,
    get_jwt_identity , jwt_required , get_jti , JWTManager
)
from flask_limiter import Limiter

from base_application import jwt
from app.api import bp
from app.api.auth import basic_auth

limiter = Limiter()
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# implemented on https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/?highlight=logout
# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None

@bp.route('/authenticate', methods=['POST'])
@limiter.limit("3/minute")
@basic_auth.login_required
def get_token():
    """ Generates a authentication and refresh token for a user """
    user_id = g.current_user.id
    email = g.current_user.email

    user = {"id": user_id, "email": email}
    ret = {
        "access_token": create_access_token(identity=user),
        "refresh_token": create_refresh_token(identity=user),
        "user": {"id": user_id, "email": email}
    }

    return jsonify(ret), 200


@bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """ Refreshes a authentication token for a user """
    user = get_jwt_identity()
    ret = {"access_token": create_access_token(identity=user)}

    return jsonify(ret), 200

@bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """Move the user's access and refresh token into the block list,
        to lock the user out and prevent session hijacking
    """
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    jti_access = get_jti(access_token)
    jti_refresh = get_jti(refresh_token)
    jwt_redis_blocklist.set(jti_access, "", ex=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    jwt_redis_blocklist.set(jti_refresh, "", ex=app.config["JWT_ACCESS_TOKEN_EXPIRES"])

    return jsonify(msg="Access and refresh token revoked"), 200


