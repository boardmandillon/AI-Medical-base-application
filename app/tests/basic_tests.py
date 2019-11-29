import unittest
from flask_testing import TestCase

from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True


class BasicTests(TestCase):
    """Class for basic test cases."""

    def create_app(self):
        self.app = create_app(TestConfig)
        return self.app

    def setUp(self):
        """Executed before starting a test."""
        self.app_context = self.app.app_context()
        self.app_context.push()

        # TODO: #11 Add database functionality to web app
        # db.create_all()

    def tearDown(self):
        """Executed after each test."""
        # TODO: #11 Add database functionality to web app
        # db.session.remove()
        # db.drop_all()

        self.app_context.pop()

    ####################
    # Unit test cases...
    ####################

    def test_main_page(self):
        response = self.client.get('/')

        self.assert200(response, message="Status code not 200")


if __name__ == "__main__":
    unittest.main()
