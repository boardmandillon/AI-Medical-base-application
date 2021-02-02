from flask import request
from flask import jsonify

from flask_jwt_extended import (fresh_jwt_required, get_jwt_identity)

from app.models.user import User
from app import db_relational as db

from app.api import bp
from app.api.errors import bad_request, forbidden
from app.auth.sendemail import send_password_reset_email


@bp.route('/users', methods=['POST'])
def create_user():
    """Create user accounts using api stores email, password, name and date of birth
    into database. Accepts POST requests with JSON and urlencoded content.
    """
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    if not data.get('email') or not data.get('password') or \
            not data.get('name'):
        return bad_request("Must include 'email', 'password', 'name'")
    elif User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    else:
        user = User()
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201


@bp.route('/users/password-reset', methods=['PUT'])
def password_reset():
    """Sends a reset password email to the given email address.

    This will always return a 204 NO CONTENT for security reasons unless
    the request is bad.
    """
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    email = data.get('email')
    if not email:
        return bad_request("Must include 'email' field")

    user = User.query.filter_by(email=email).first()
    if user:
        send_password_reset_email(user)
    return jsonify(), 204


@bp.route('/users/password', methods=['PUT'])
@fresh_jwt_required
def password():
    """Changes the password to the given new password for the user
    corresponding to the given password reset token.

    If the token is invalid a 403 FORBIDDEN is returned.
    """
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    identity = get_jwt_identity()
    new_password = data.get('new_password')
    if not new_password:
        return bad_request("Must include 'token' and 'new_password' fields")

    user = User.verify_reset_password_token(identity)
    if user:
        user.set_password(new_password)
        db.session.commit()
        return jsonify(), 204
    else:
        return forbidden("Invalid password reset token")
