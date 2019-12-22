from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db_relational as db, login


class User(UserMixin, db.Model):
    """Database model representing a user."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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


@login.user_loader
def load_user(_id):
    """Retrieves a user by their ID, used by flask-login."""
    return User.query.get(int(_id))
