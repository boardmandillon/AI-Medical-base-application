import os
import unittest

from app import db_relational as db
from app.models.user import User


class setUp():
    """Class for basic test database."""
    def setUpTestUser():
        user = User()
        data=dict(email="user@email.com", password="password", name="name")
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()