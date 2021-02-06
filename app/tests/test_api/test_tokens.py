import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from app.models.user import User
from app.api import tokens


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class TokensTest(unittest.TestCase):
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
    def test_get_token(self):
        setUp.setUpTestUser()
        response = self.get_token()

        self.assertEqual(response.status_code, 200)

    def test_refresh_token(self):
        setUp.setUpTestUser()
        authentication_token = json.loads(self.get_token().data)
        refresh_token = authentication_token["refresh_token"]

        response = self.refresh_token(refresh_token)

        self.assertEqual(response.status_code, 200)


    # helper methods
    ############################################################################
    def get_token(self):
        return self.app.test_client().post(
            '/api/authenticate',
            headers = {
                'Authorization': 'Basic dXNlckBlbWFpbC5jb206cGFzc3dvcmQ=' # base64 encoded (user@email.com:password)
            }
        )

    def refresh_token(self, refresh_token):
        return self.app.test_client().post(
            '/api/refresh',
            headers = {
                'Authorization': f'Bearer {refresh_token}'
            }
        )




if __name__ == "__main__":
    unittest.main()