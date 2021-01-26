import os
import unittest

from app import create_app, db_relational as db
from setup import setUp
from config import Config, basedir


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class BasicTest(unittest.TestCase):
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
    def test_valid_user_registration(self):
        response = self.register(
            'user@email.com',
            'password',
            'Test McTest'
        )

        self.assertEqual(response.status_code, 201)

    def test_duplicate_user_registration(self):
        setUp.setUpTestUser()

        response = self.register(
            'user@email.com',
            'password',
            'Test McTest'
        )

        self.assertEqual(response.status_code, 400)

    def test_valid_user_login(self):
        setUp.setUpTestUser()
        response = self.login('user@email.com', 'password')

        self.assertEqual(response.status_code, 200)

    def test_valid_user_logout(self):
        setUp.setUpTestUser()
        self.login('user@email.com', 'password')

        response = self.logout()

        self.assertEqual(response.status_code, 200)

    def test_valid_token_Authentication(self):
        setUp.setUpTestUser()
        response = self.authenticate_token()

        self.assertEqual(response.status_code, 200)

    # def test_valid_token_Refresh(self):
    #     setUp.setUpTestUser()
    #     authentication_token = self.authenticate_token()

    #     response = self.refresh_token(authentication_token)

    #     self.assertEqual(response.status_code, 200)
    ############################################################################

    # helper methods
    ############################################################################
    def register(self, email, password, name):
        return self.app.test_client().post(
            '/api/users',
            data=dict(email=email, password=password, name=name)
        )

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

    def verify_password(self, email, password):
        return self.app.test_client().get(
            'auth/login',
            data=dict(email=email, password=password)
        )

    def authenticate_token(self):
        return self.app.test_client().post(
            '/api/authenticate',
            headers = {
                'Authorization': 'Basic dXNlckBlbWFpbC5jb206cGFzc3dvcmQ=' # base64 encoded (user@email.com:password)
            }
        )

    # def refresh_token(self):
    #     return self.app.test_client().post(
    #         '/api/authenticate',
    #         headers = {
    #             'Authorization': 'Basic dXNlckBlbWFpbC5jb206cGFzc3dvcmQ=' # base64 encoded (user@email.com:password)
    #         }
    #     )
    ############################################################################

    # dummy tests
    ############################################################################
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
    
    def test_islower(self):
        self.assertTrue('foo'.islower())

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
    ############################################################################

if __name__ == "__main__":
    unittest.main()