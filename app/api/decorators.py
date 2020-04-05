from flask import g

from functools import wraps

from .errors import forbidden


def user_role_required(user_role):
    """Wrapper for checking the user has the correct permissions when
    accessing the API.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.has_user_role(user_role):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
