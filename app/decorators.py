from flask import abort
from flask_login import current_user

from functools import wraps

from app.models.user import UserRoles


def user_role_required(user_role):
    """Wrapper for checking the user has the correct permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_user_role(user_role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return user_role_required(UserRoles.ADMIN)(f)
