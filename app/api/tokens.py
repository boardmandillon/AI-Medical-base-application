import redis
from flask import current_app as app
from flask import jsonify, g, request
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jti,
    get_jwt
)

from app import limiter, jwt
from app.api import bp
from app.api.auth import basic_auth

jwt_redis_blocklist = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

# implemented on https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/?highlight=logout
# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(_, jwt_payload):
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
@jwt_required(refresh=True)
def refresh():
    """ Refreshes a authentication token for a user """
    user = get_jwt_identity()
    ret = {"access_token": create_access_token(identity=user)}

    return jsonify(ret), 200


# Endpoint for revoking the current users access token. Save the JWTs unique
# identifier (jti) in redis. Also set a Time to Live (TTL) when storing the JWT
# so that it will automatically be cleared out of redis after the token expires.
@bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    """ Move the user's access and refresh token into the block list """
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    jti_access = get_jwt()["jti"]
    jti_refresh = get_jti(data['refresh_token'])

    jwt_redis_blocklist.set(jti_access, "", ex=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    jwt_redis_blocklist.set(jti_refresh, "", ex=app.config["JWT_REFRESH_TOKEN_EXPIRES"])

    return jsonify(msg="Access and refresh token revoked"), 200

