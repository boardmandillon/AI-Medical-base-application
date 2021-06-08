import json
import os
import unittest

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir


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
    def test_get_tokens(self):
        setUp.setUpTestUser()
        response = self.get_tokens()

        self.assertEqual(response.status_code, 200)

    def test_token_refresh(self):
        setUp.setUpTestUser()
        data = json.loads(self.get_tokens().data)

        refresh_token = data["refresh_token"]
        response = self.refresh(refresh_token)

        self.assertEqual(response.status_code, 200)

    def test_token_blocklist(self):
        setUp.setUpTestUser()
        data = json.loads(self.get_tokens().data)

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        self.logout(access_token, refresh_token)
        response = self.refresh(refresh_token)

        self.assertEqual(response.status_code, 401)

    # helper methods
    ############################################################################
    def get_tokens(self):
        return self.app.test_client().post(
            '/api/authenticate',
            headers={'Authorization': 'Basic dXNlckBlbWFpbC5jb206cGFzc3dvcmQ='}  # base64 encoded (user@email.com:password)
        )

    def refresh(self, refresh_token):
        return self.app.test_client().post(
            '/api/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )

    def logout(self, access_token, refresh_token):
        return self.app.test_client().delete(
            '/api/logout',
            headers={'Authorization': f'Bearer {access_token}'},
            data=dict(refresh_token=refresh_token)
        )


if __name__ == "__main__":
    unittest.main()
