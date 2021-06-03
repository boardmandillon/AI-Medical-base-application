import redis
from flask import jsonify , g
from flask_jwt_extended import (
    jwt_refresh_token_required ,
    create_access_token ,
    create_refresh_token ,
    get_jwt_identity , jwt_required , get_jti
)
from flask_limiter import Limiter

from app.api import bp
from app.api.auth import basic_auth
from base_application import app

limiter = Limiter()
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

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

@bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_jti()
    jwt_redis_blocklist.set(jti, "", ex=app.config.keys("JWT_ACCESS_TOKEN_EXPIRES"))
    return jsonify(msg="Access token revoked"), 200


