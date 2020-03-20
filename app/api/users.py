from flask import request
from flask import jsonify

from app.models.user import User
from app import db_relational as db

from app.api import bp
from app.api.errors import bad_request


@bp.route('/users', methods=['POST'])
def create_user():
    """Create user accounts using api stores email and password
    into database.
    """
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        data = request.form.to_dict() or {}
    elif request.headers['Content-Type'] == 'application/json':
        data = request.get_json() or {}

    if not data.get('email') or not data.get('password') or not data.get('name') \
            or not data.get('date_of_birth'):
        return bad_request('must include email, password, name and date of birth fields')
    elif User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    else:
        user = User()
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()
        response = jsonify(user.to_dict())
        response.status_code = 201
        return response
