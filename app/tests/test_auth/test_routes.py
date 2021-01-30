import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from unittest.mock import patch
from app.models.user import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class RoutesTest(unittest.TestCase):
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
 
    def test_valid_user_login(self):
        setUp.setUpTestUser()

        response = self.login(
            'user@email.com',
            'password'
        )

        self.assertEqual(response.status_code, 200)

    def test_valid_user_logout(self):
        setUp.setUpTestUser()
        self.login('user@email.com', 'password')

        response = self.logout()

        self.assertEqual(response.status_code, 200)


    ############################################################################

    # helper methods
    ############################################################################

    def login(self, email, password):
        return self.app.test_client().get(
            'auth/login',
            data=dict(email=email, password=password)
        )

    def logout(self):
        return self.app.test_client().get(
            'auth/logout',
            follow_redirects=True
        )
    ############################################################################





if __name__ == "__main__":
    unittest.main()