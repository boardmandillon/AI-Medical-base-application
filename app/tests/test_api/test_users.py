import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from unittest.mock import patch
from app.models.user import User
from app.auth.sendemail import create_password_reset_token


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')


class UsersTest(unittest.TestCase):
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
    def test_create_user_returns201_andCorrectUserData_whenValid(self):
        response = self.register(
            'user@email.com',
            'password',
            'Test McTest'
        )

        response_data = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['email'], 'user@email.com')
        self.assertEqual(response_data['id'], 1)
        self.assertEqual(response_data['name'], 'Test McTest')

    def test_create_user_addsUserToDB_whenValid(self):
        self.register(
            'user@email.com',
            'password',
            'Test McTest'
        )

        self.assertEqual(User.query.get(1).name, 'Test McTest')
        self.assertEqual(User.query.get(1).email, 'user@email.com')

    def test_create_user_returns400AndErrorMessage_whenDuplicateEmailRegisters(self):
        setUp.setUpTestUser()

        response = self.register(
            'user@email.com',
            'password',
            'Test McTest'
        )

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_message, 'Please use a different email address')

    def test_create_user_returns400AndErrorMessage_whenMissingEmail(self):
        response = self.register(
            None,
            'password',
            'Test McTest'
        )

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_message, "Must include 'email', 'password', 'name'")

    def test_create_user_returns400AndErrorMessage_whenMissingName(self):
        response = self.register(
            'user@email.com',
            'password',
            None
        )

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_message, "Must include 'email', 'password', 'name'")

    def test_create_user_returns400AndErrorMessage_whenMissingPassword(self):
        response = self.register(
            'user@email.com',
            None,
            'Test McTest'
        )

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_message, "Must include 'email', 'password', 'name'")

    def test_password_reset_returns204_whenValidRequest(self):
        response = self.reset_password_request(
            'user@email.com'
        )

        self.assertEqual(response.status_code, 204)

    @patch('app.api.users.send_password_reset_email')
    def test_password_reset_callsSendEmailToCorrectUser_whenValidRequest(self, test_patch):
        setUp.setUpTestUser()
        self.reset_password_request(
            'user@email.com'
        )

        test_patch.assert_called_with(User.query.get(1))

    @patch('app.api.users.send_password_reset_email')
    def test_password_reset_doesNotSendEmail_whenUserDoesNotExist(self, test_patch):
        self.reset_password_request(
            'user@email.com'
        )

        assert not test_patch.called, 'send_password_reset_email was called and should not have been'

    def test_password_reset_returns400AndErrorMessage_whenMissingEmail(self):
        response = self.reset_password_request(
            None
        )

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_message, "Must include 'email' field")

    @patch('app.api.users.User.verify_reset_password_token')
    def test_password_returns204_whenValidNewPasswordRequest(self, test_patch):
        setUp.setUpTestUser()
        user = User.query.get(1)

        password_reset_token = create_password_reset_token(user)

        response = self.set_new_password(
            password_reset_token,
            'newPassword'
        )

        self.assertEqual(response.status_code, 204)

    @patch('app.api.users.User.verify_reset_password_token')
    def test_password_doesNotCallsSetPassword_whenUserDoesNotExist(self, test_patch):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.id = 999
        password_reset_token = create_password_reset_token(user)

        test_patch.return_value = False

        response = self.set_new_password(
            password_reset_token,
            'newPassword'
        )

        self.assertEqual(response.status_code, 403)

    def test_password_returns403AndErrorMessage_wheninvalidPasswordResetToken(self):
        response = self.set_new_password(
            'invalidToken',
            'newPassword'
        )

        self.assertEqual(response.status_code, 422)

    @patch('app.api.users.User.verify_reset_password_token')
    def test_password_returns400AndErrorMessage_whenMissingToken(self, test_patch):
        setUp.setUpTestUser()
        test_patch.return_value = User.query.get(1)

        response = self.set_new_password(
            None,
            'newPassword'
        )

        self.assertEqual(response.status_code, 422)

    # helper methods
    ############################################################################
    def register(self, email, password, name):
        return self.app.test_client().post(
            '/api/users',
            data=dict(email=email, password=password, name=name)
        )

    def reset_password_request(self, email):
        return self.app.test_client().put(
            '/api/users/password-reset',
            data=dict(email=email)
        )

    def set_new_password(self, token, new_password):
        return self.app.test_client().put(
            '/api/users/password',
            headers={
                'Authorization': f'Bearer {token}'
            },
            data=dict(new_password=new_password)
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


if __name__ == "__main__":
    unittest.main()
