from flask import request
from flask import url_for
from flask import jsonify

from app import db_relational as db
from app.models import User

from app.api import bp
from app.api.errors import bad_request

@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['POST'])
def create_user():
    """Create user."""
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        return bad_request('must include email and password fields')
    elif User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    else:
        user = User()
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()
        response = jsonify(user.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('api.get_user', id=user.id)
        return response
    
