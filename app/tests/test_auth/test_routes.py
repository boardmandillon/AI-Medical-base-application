import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from unittest.mock import patch
from app.models.user import User, UserRoles
from flask import url_for

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'test.localdomain'

class RoutesTest(unittest.TestCase):
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
    def test_302_redirectsToLogin_whenFormDoesNotValidateOnSubmit(self):    #not authenticated, redirected to sign in
        setUp.setUpTestUser()
        
        response = self.login_get(
            'user@email.com',
            'password'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In - Vulture', response.data)

    @patch('flask_login.utils._get_user')
    def test_302_redirectsToAdmin_whenUserAlreadyAuthenticated(self, current_user_patch):
        setUp.setUpTestUser()
        current_user_patch.return_value = User.query.get(1)
             
        response = self.login_get(
            'user@email.com',
            'password'
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('admin.index', _external=True))


    def test_302_redirectsToLogin_whenUserDoesNotExist(self):

        response = self.login_post(
            'user@email.com',
            'password'
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('auth.login', _external=True))
    

    def test_302_redirectsToLogin_whenIncorrectPassword(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.ADMIN
        
        response = self.login_post(
            'user@email.com',
            'incorrectPassword'
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('auth.login', _external=True))

    def test_302_redirectsToLogin_whenUserNotAdmin(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.EXPERT
        
        response = self.login_post(
            'user@email.com',
            'password'
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('auth.login', _external=True))

    def test_302_redirectsToAdminIndex_whenValidAdmin_andNoPageSet(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.ADMIN
        
        response = self.login_post(
            'user@email.com',
            'password'   
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('admin.index', _external=True))

    def test_302_redirectsToNextPage_whenSafePageSet(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.ADMIN
        
        response = self.app.test_client().post(
            'auth/login?next=nextPage',
            data=dict(email="user@email.com", password="password", remember_me=True, submit=True),
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://test.localdomain/auth/nextPage')

    def test_302_redirectsToAdmin_whenMaliciousPageSet(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        user.user_role = UserRoles.ADMIN
        
        response = self.app.test_client().post(
            'auth/login?next=',
            data=dict(email="user@email.com", password="password", remember_me=True, submit=True),
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('admin.index', _external=True))




    def test_valid_user_logoutReturns302AndRedirectstoLogin_whenValidRequest(self):
        setUp.setUpTestUser()
        self.login_get('user@email.com', 'password')

        response = self.logout()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('auth.login', _external=True))         

    ############################################################################

    # helper methods
    ############################################################################

    def login_get(self, email, password):
        return self.app.test_client().get(
            'auth/login',
            data=dict(email=email, password=password)
        )

    def login_post(self, email, password):
        return self.app.test_client().post(
            'auth/login',
            data=dict(email=email, password=password, remember_me=True, submit=True),
        )

    def logout(self):
        return self.app.test_client().get(
            'auth/logout'
        )

    
    ############################################################################





if __name__ == "__main__":
    unittest.main()