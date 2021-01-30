import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from app.models.user import User, UserRoles
from app.api import decorators
from flask import g


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class RoleDecoratorsTest(unittest.TestCase):
    """Class for basic test cases."""
    
    def setUp(self):
        "set up test fixtures"
        app = create_app(TestConfig)

        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

        with self.app_context:
            db.create_all()

    def tearDown(self):
        """Executed after each test."""
        with self.app_context:
            db.session.remove()
            db.drop_all()

    # Unit test cases
    ############################################################################
    # USER = 1    
    # EXPERT = 2
    # ADMIN = 4

    def test_user_role_required_runsFunction_whenHigherRole(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.ADMIN
        g.current_user = user

        response = self.does_function_run()

        self.assertEqual(response, True)

    def test_user_role_required_runsFunction_whenCorrectRole(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.EXPERT
        g.current_user = user

        response = self.does_function_run()

        self.assertEqual(response, True)

    
    def test_user_role_required_returns403Forbidden_whenUserHasWrongRole(self):
        #default user role is USER, which has less privilege than expert and admin
        setUp.setUpTestUser()
        g.current_user = User.query.get(1)

        response = self.does_function_run()
        
        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_message,"Insufficient permissions")

    ############################################################################

    # helper methods
    ############################################################################
    @decorators.user_role_required(UserRoles.EXPERT)
    def does_function_run(self):
        return True

    ############################################################################


if __name__ == "__main__":
    unittest.main()