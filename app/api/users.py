from flask import request

from app.api import bp
from app.models import User


@bp.route('/users', methods=['POST'])
def create_user():
    """Create user."""
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        # Must include email and password fields
        return None  # TODO: #12 Add error handling to the web app
    elif User.query.filter_by(email=data['email']).first():
        # Please use a different email address
        return None  # TODO: #12 Add error handling to the web app
    else:
        user = User()
        user.from_dict(data, new_user=True)
