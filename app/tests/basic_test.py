import unittest
from flask import Flask
from flask_testing import TestCase, LiveServerTestCase

from app import create_app
from config import Config


# class TestConfig(Config):
#     TESTING = True


class BasicTest(TestCase):
    """Class for basic test cases."""

    def create_app(self):
        # self.app = create_app(TestConfig)
        # return self.app
        app = Flask(__name__)
        app.config['TESTING'] = True

        #liveservertestcase
        return app

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

    def test_main_page_returns_fail(self):
        response = self.client.get('/')

        # self.assert200(response, message="Status code not 200")
        self.assert404(response, message="Status code not 200")

    def test_admin_page_returns_success(self):
        # response = self.client.get('/admin', follow_redirects=True)
        # self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/admin')
        self.assertEqual(response.status_code, 200)





    ########################
    #### helper methods ####
    ########################
    

    def login(self, email, password):
        return self.app.test_client().post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )
    
    def logout(self):
        return self.app.test_client().get(
            '/logout',
            follow_redirects=True)

    def test_valid_user_registration(self):
        response = self.login('patkennedy79@gmail.com', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
    
    def test_valid_logout(self):
        response = self.logout()
        self.assertEqual(response.status_code, 200)


    ## dummy tests
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
    
    def test_islower(self):
        self.assertTrue('foo'.islower())

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO') 


if __name__ == "__main__":
    unittest.main()