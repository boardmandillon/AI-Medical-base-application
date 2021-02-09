from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app import db_relational as db, login

import enum


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
    name = db.Column(db.String(40), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    date_of_birth = db.Column(db.Date, index=True)
    date_registered = db.Column(
        db.DateTime, index=True,
        default=datetime.utcnow().replace(microsecond=0)
    )
    last_login = db.Column(db.DateTime, index=True)
    password_hash = db.Column(db.String(128))
    user_role = db.Column(
        db.Enum(UserRoles),
        default=UserRoles.USER, nullable=False
    )

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
        for field in ['email', 'name', 'date_of_birth']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def has_user_role(self, user_role):
        """Checks if the user has the permissions level of at least the
        given role. See the UserRoles class.
        """
        return self.user_role.value >= user_role.value

    def is_admin(self):
        """Checks if the user is an admin."""
        return self.user_role == UserRoles.ADMIN

    @staticmethod
    def verify_reset_password_token(token):
        """Verifies the given password reset token, returning the user
        corresponding to the token if one exists.

        :param token: Password reset token.
        """
        user = User.query.filter_by(id=token.user_id).first()

        if token.action == "password_reset" and user:
            return user
        else:
            return None


@login.user_loader
def load_user(_id):
    """Retrieves a user by their ID, used by flask-login."""
    return User.query.get(int(_id))
