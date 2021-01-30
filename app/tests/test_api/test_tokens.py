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

    
    # def test_get_token_returnsUserToken_whenValidUser(self):
    #     setUp.setUpTestUser()
    #     response = self.post_token()
    #     print("response", response)



    # helper methods
    ############################################################################
    # def post_token(self):
    #     return self.app.test_client().post(
    #         '/api/tokens'
    #     )
        


    ############################################################################



if __name__ == "__main__":
    unittest.main()