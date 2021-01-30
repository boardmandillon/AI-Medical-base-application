import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from app.models.user import User
from app.api import errors


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class ErrorsTest(unittest.TestCase):
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
    def test_error_response_returnsCorrectStatusAndMessage_whenValidInput(self):
        response = errors.error_response(200, "test error response message")

        response_message = json.loads(response.get_data().decode("utf-8"))['message']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response_message, "test error response message")
    
    def test_error_response_returnsCorrectStatusAndMessage_whenNoMessage(self):
        response = errors.error_response(200)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status, "200 OK")
    
    def test_error_response_returnsCodeAndUnknown_whenUnknownStatusCodeNoMessage(self):
        response = errors.error_response(2021)

        response_error_message = json.loads(response.get_data().decode("utf-8"))['error']

        self.assertEqual(response.status_code, 2021)
        self.assertEqual(response.status, "2021 UNKNOWN")
        self.assertEqual(response_error_message, "Unknown error")
    
    def test_error_response_returnsCodeAndMessageAndUnknown_whenUnknownStatusCodeAndMessage(self):
        response = errors.error_response(2021, "2021 test message")

        response_error_message = json.loads(response.get_data().decode("utf-8"))['error']
        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 2021)
        self.assertEqual(response.status, "2021 UNKNOWN")
        self.assertEqual(response_error_message, "Unknown error")
        self.assertEqual(response_message, "2021 test message")




    def test_forbidden_returns403AndMessage_whenValidInput(self):
        response = errors.forbidden("test forbidden message")

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.status, "403 FORBIDDEN")
        self.assertEqual(response_message, "test forbidden message")
    
    def test_forbidden_returns403_whenNoMessage(self):
        response = errors.forbidden(None)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.status, "403 FORBIDDEN")
        




    def test_unauthorized_returns401AndMessage_whenValidInput(self):
        response = errors.unauthorized("test unauthorized message")

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.status, "401 UNAUTHORIZED")
        self.assertEqual(response_message, "test unauthorized message")
    
    def test_unauthorized_returns401_whenNoMessage(self):
        response = errors.unauthorized()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.status, "401 UNAUTHORIZED")
    



    def test_bad_request_returns403AndMessage_whenValidInput(self):
        response = errors.bad_request("test bad request message")

        response_message = json.loads(response.get_data().decode("utf-8"))['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response_message, "test bad request message")
    
    def test_bad_request_returns403_whenNoMessage(self):
        response = errors.bad_request(None)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.status, "400 BAD REQUEST")


    ############################################################################



if __name__ == "__main__":
    unittest.main()