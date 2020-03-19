from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import base64
from datetime import datetime, timedelta
import os
import enum

from app import db_relational as db, login


class UserRoles(enum.Enum):
    """Class for defining the possible different user roles.

    User roles:
        USER: A standard user, should be allowed to submit data to be
            diagnosed.
        EXPERT: A user who is authorised to give the real diagnosis of
            symptoms once they have been diagnosed by a medical professional.
            It is important to ensure that data is being correctly labelled
            so that the machine learning models can learn, however some
            projects may allow any users to label their previously submitted
            diagnoses.
        ADMIN: A user who can access the admin interface.
    """
    USER = 1
    EXPERT = 2
    ADMIN = 4


class User(UserMixin, db.Model):
    """Database model representing a user."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    user_role = db.Column(
        db.Enum(UserRoles), default=UserRoles.USER, nullable=False)

    def __repr__(self):
        """Return print information about the user in a
        debug friendly way.
        """
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        """Set password hash using the given password.

        :param password: Password to use.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against stored password hash.

        :param password: Password to use.
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Create a JSON representation of user."""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
        return data

    def from_dict(self, data, new_user=False):
        """Construct a user object from a dictionary.

        :param data: Dictionary of user information.
        :param new_user: Whether the user is new, if True the password field
            is set, default is False.
        """
        for field in ['email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        """Returns a randomly string token to the user."""
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        """Make a token assigned to user invalid."""
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """Finds the user of the given token."""
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def has_user_role(self, user_role):
        """Checks if the user has the permissions level of at least the
        given role. See the UserRoles class.
        """
        return self.user_role.value >= user_role.value


@login.user_loader
def load_user(_id):
    """Retrieves a user by their ID, used by flask-login."""
    return User.query.get(int(_id))
