import os
import unittest

from app import db_relational as db
from app.models.user import User, UserRoles


class setUp():
    """Class for basic test database."""
    def setUpTestUser():
        user = User()
        data=dict(email="user@email.com", password="password", name="name")
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()

    def setUpTestAdmin():
        user = User()
        data=dict(email="admin@email.com", password="adminPassword", name="admin")
        user.from_dict(data, new_user=True)
        user.user_role = UserRoles.ADMIN
        db.session.add(user)
        db.session.commit()

    def setUpTestExpert():
        user = User()
        data=dict(email="expert@email.com", password="expertPassword", name="expert")
        user.from_dict(data, new_user=True)
        user.user_role = UserRoles.EXPERT
        db.session.add(user)
        db.session.commit()