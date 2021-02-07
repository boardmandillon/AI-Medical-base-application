import os
import unittest
import json
import sys

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from unittest.mock import patch, call
from app.models.user import User
from app.commands import cli_admin
from io import StringIO

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class CliAdminTest(unittest.TestCase):
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
    @patch('sys.exit')
    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_create_superuser_createsUserAndAddsToDB_whenValidRegistration(self, input_patch, getpass_patch, patch_exit):
        # create one user so we are not calling filter by first on an empty db
        setUp.setUpTestUser()
        patch_exit.return_value = None   # stops the function calling system exit

        #mocking command line inputs
        input_patch.side_effect=['admin', 'admin@email.com']
        getpass_patch.side_effect = ['adminPassword', 'adminPassword']

        cli_admin.create_superuser()

        self.assertEqual(User.query.get(2).name, "admin")
        self.assertEqual(User.query.get(2).email, "admin@email.com")

    @patch('sys.exit')
    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_create_superuser_printsCorrectMessage_whenWrongConfirmPassword(self, input_patch, getpass_patch, patch_exit):
        # create one user so we are not calling filter by first on an empty db
        setUp.setUpTestUser()
        patch_exit.return_value = None   # stops the function calling system exit
        captured_output = StringIO()
        sys.stdout = captured_output

        #mocking command line inputs
        input_patch.side_effect=['admin', 'admin@email.com']
        getpass_patch.side_effect = ['adminPassword', 'unmatchingPassword']

        cli_admin.create_superuser()
        sys.stdout = sys.__stdout__

        self.assertEqual(captured_output.getvalue(), 'Passwords are not the same\n')

    @patch('sys.exit')
    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_create_superuser_printsCorrectMessage_whenMissingName(self, input_patch, getpass_patch, patch_exit):
        # create one user so we are not calling filter by first on an empty db 
        setUp.setUpTestUser()
        patch_exit.return_value = None   # stops the function calling system exit 
        captured_output = StringIO()
        sys.stdout = captured_output

        #mocking command line inputs
        input_patch.side_effect=[None, 'admin@email.com']
        getpass_patch.side_effect = ['adminPassword', 'adminPassword']

        cli_admin.create_superuser()
        sys.stdout = sys.__stdout__

        self.assertEqual(captured_output.getvalue(), 'Must include email, password and name fields\n')

    @patch('sys.exit')
    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_create_superuser_printsCorrectMessage_whenMissingEmail(self, input_patch, getpass_patch, patch_exit):
        # create one user so we are not calling filter by first on an empty db
        setUp.setUpTestUser()
        patch_exit.return_value = None   # stops the function calling system exit
        captured_output = StringIO()
        sys.stdout = captured_output

        #mocking command line inputs
        input_patch.side_effect=['admin', None]
        getpass_patch.side_effect = ['adminPassword', 'adminPassword']

        cli_admin.create_superuser()
        sys.stdout = sys.__stdout__

        self.assertEqual(captured_output.getvalue(), 'Must include email, password and name fields\n')

    @patch('sys.exit')
    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_create_superuser_printsCorrectMessage_whenMissingPassword(self, input_patch, getpass_patch, patch_exit):
        # create one user so we are not calling filter by first on an empty db 
        setUp.setUpTestUser()

        patch_exit.return_value = None   # stops the function calling system exit 
        captured_output = StringIO()
        sys.stdout = captured_output

        #mocking command line inputs
        input_patch.side_effect=['admin', 'admin@email.com']
        getpass_patch.side_effect = [None, None]

        cli_admin.create_superuser()
        sys.stdout = sys.__stdout__

        self.assertEqual(captured_output.getvalue(), 'Must include email, password and name fields\n')

    @patch('sys.exit')
    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_create_superuser_printsCorrectMessage_whenUserEmailAlreadyExists(self, input_patch, getpass_patch, patch_exit):
        # create existing admin user
        setUp.setUpTestAdmin()

        patch_exit.return_value = None   # stops the function calling system exit
        captured_output = StringIO()
        sys.stdout = captured_output

        #mocking command line inputs
        input_patch.side_effect=['admin', 'admin@email.com']
        getpass_patch.side_effect = ['adminPassword', 'adminPassword']

        cli_admin.create_superuser()
        sys.stdout = sys.__stdout__

        self.assertEqual(captured_output.getvalue(), 'please use a different email address\n')




    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_login_returnsUser_whenValidAdminLogin(self, input_patch, getpass_patch):
        setUp.setUpTestAdmin()

        #mocking command line inputs
        input_patch.return_value = "admin@email.com"
        getpass_patch.return_value = "adminPassword"

        response = cli_admin.login()

        self.assertEqual(response, User.query.get(1))

    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_login_returnsNoneAndPrintsCorrectMessage_whenMissingEmail(self, input_patch, getpass_patch):
        setUp.setUpTestAdmin()

        #mocking command line inputs
        input_patch.return_value = None
        getpass_patch.return_value = "adminPassword"
        captured_output = StringIO()
        sys.stdout = captured_output

        response = cli_admin.login()
        sys.stdout = sys.__stdout__

        self.assertEqual(response, None)
        self.assertEqual(captured_output.getvalue(), 'Please enter your Admin email and password\n')

    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_login_returnsNoneAndPrintsCorrectMessage_whenMissingPassword(self, input_patch, getpass_patch):
        setUp.setUpTestAdmin()

        #mocking command line inputs
        input_patch.return_value = "admin@email.com"
        getpass_patch.return_value = None
        captured_output = StringIO()
        sys.stdout = captured_output

        response = cli_admin.login()
        sys.stdout = sys.__stdout__

        self.assertEqual(response, None)
        self.assertEqual(captured_output.getvalue(), 'Please enter your Admin email and password\n')

    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_login_returnsNoneAndPrintsCorrectMessage_whenUserEmailDoesNotExist(self, input_patch, getpass_patch):
        setUp.setUpTestAdmin()

        #mocking command line inputs
        input_patch.return_value = "ghost@email.com"
        getpass_patch.return_value = "adminPassword"
        captured_output = StringIO()
        sys.stdout = captured_output

        response = cli_admin.login()
        sys.stdout = sys.__stdout__

        self.assertEqual(response, None)
        self.assertEqual(captured_output.getvalue(), 'Please enter a valid admin email and password\n')

    @patch("app.commands.cli_admin.getpass")
    @patch("app.commands.cli_admin.input")
    def test_login_returnsNoneAndPrintsCorrectMessage_whenIncorrectPassword(self, input_patch, getpass_patch):
        setUp.setUpTestAdmin()

        #mocking command line inputs
        input_patch.return_value = "admin@email.com"
        getpass_patch.return_value = "wrongPassword"
        captured_output = StringIO()
        sys.stdout = captured_output

        response = cli_admin.login()
        sys.stdout = sys.__stdout__

        self.assertEqual(response, None)
        self.assertEqual(captured_output.getvalue(), 'Please enter a valid admin email and password\n')

    ############################################################################


if __name__ == "__main__":
    unittest.main()