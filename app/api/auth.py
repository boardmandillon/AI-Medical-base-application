from flask import g
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth

from app.models.user import User
from app.api.errors import unauthorized

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email, password):
    """Uses the email and password to verify a user."""
    user = User.query.filter_by(email=email).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


@token_auth.verify_token
def verify_token(token):
    """Verify that the token belongs to the user."""
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None


@basic_auth.error_handler
def basic_auth_error():
    """Simply returns a unauthorized HTTP error."""
    return unauthorized()
