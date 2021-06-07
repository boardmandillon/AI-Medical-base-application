import os
import unittest

from app import create_app, db_relational as db
from app.api import auth
from app.tests.setup import setUp
from config import Config, basedir


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')


class AuthTest(unittest.TestCase):
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

    def test_verify_password_returnsTrue_whenValidEmailPassword(self):
        setUp.setUpTestUser()

        response = auth.verify_password('user@email.com', 'password')

        self.assertEqual(response, True)

    def test_verify_password_returnsFalse_whenUserEmailDoesNotExist(self):
        response = auth.verify_password('user@email.com', 'password')

        self.assertEqual(response, False)

    def test_verify_password_returnsFalse_whenIncorrectPassword(self):
        setUp.setUpTestUser()

        response = auth.verify_password('user@email.com', 'incorrectPassword')

        self.assertEqual(response, False)

    def test_basic_auth_error_returnsHTTPError(self):
        response = auth.basic_auth_error()

        self.assertEqual(response.status_code, 401)

    ############################################################################


if __name__ == "__main__":
    unittest.main()
