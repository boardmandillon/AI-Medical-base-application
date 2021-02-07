import os
import unittest
import json

from app import create_app, db_relational as db
from app.tests.setup import setUp
from config import Config, basedir
from unittest.mock import patch
from app.models.user import User, UserRoles, load_user

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class TestToken():
    def __init__(self, user_id, action):
        self.user_id = user_id
        self.action = action

class UserTest(unittest.TestCase):
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
    def test_repr_returnsCorrectInfoWhenValidUser(self):
        setUp.setUpTestUser()
        response = User.query.get(1).__repr__() 
        self.assertEqual(response,"<User user@email.com>")
    
    @patch('app.models.user.generate_password_hash')
    def test_set_password_callsGeneratePasswordHash_withCorrectPrameter(self, hash_patch):
        user = User()

        user.set_password('password')

        hash_patch.assert_called_with('password')
    
    def test_set_password_setsHashedPasswordDifferentToOriginal_andContainsSha256(self):
        user = User()

        user.set_password('password')
        
        self.assertNotEqual(user.password_hash, 'password')
        self.assertIn('sha256', user.password_hash)

    def test_check_password_returnsTrue_whenCorrectPassword(self):
        user = User()
        user.set_password('password')

        response = user.check_password('password')

        self.assertEqual(response, True)

    def test_check_password_returnsFalse_whenIncorrectPassword(self):
        user = User()
        user.set_password('password')

        response = user.check_password('wrongPassword')

        self.assertEqual(response, False)
    
    def test_to_dict_createsJSONRepresentationOfUser_whenValidUser(self):
        setUp.setUpTestUser()
        user = User.query.get(1)
        expected_response = eval("{'id': 1, 'name': 'name', 'email': 'user@email.com'}")

        response = user.to_dict()

        self.assertEqual(response, expected_response)
    
    def test_to_dict_createsJSONWithNoneFields_whenInvalidUser(self):
        user = User()
        expected_response = eval("{'id': None, 'name': None, 'email': None}")

        response = user.to_dict()

        self.assertEqual(response, expected_response)

    def test_from_dict_constructsUserObject_whenAllFieldsProvided(self):
        user = User()
        data=dict(email="user@email.com", password="password", name="name")

        user.from_dict(data, new_user=True)

        self.assertEqual(user.name, 'name')
        self.assertEqual(user.email, 'user@email.com')
    
    def test_has_user_role_returnsTrue_ifUserIsUserAndTestForUser(self):
        self._test_has_user_role_with(UserRoles.USER, UserRoles.USER, True)
    
    def test_has_user_role_returnsTrue_ifUserIsUserAndTestForExpert(self):
        self._test_has_user_role_with(UserRoles.USER, UserRoles.EXPERT, False)
    
    def test_has_user_role_returnsTrue_ifUserIsUserAndTestForAdmin(self):
        self._test_has_user_role_with(UserRoles.USER, UserRoles.ADMIN, False)
    
    def test_has_user_role_returnsTrue_ifUserIsExpertAndTestForUser(self):
        self._test_has_user_role_with(UserRoles.EXPERT, UserRoles.USER, True)
    
    def test_has_user_role_returnsTrue_ifUserIsExpertAndTestForExpert(self):
        self._test_has_user_role_with(UserRoles.EXPERT, UserRoles.EXPERT, True)
    
    def test_has_user_role_returnsTrue_ifUserIsExpertAndTestForAdmin(self):
        self._test_has_user_role_with(UserRoles.EXPERT, UserRoles.ADMIN, False)
    
    def test_has_user_role_returnsTrue_ifUserIsAdminAndTestForUser(self):
        self._test_has_user_role_with(UserRoles.ADMIN, UserRoles.USER, True)
    
    def test_has_user_role_returnsTrue_ifUserIsAdminAndTestForExpert(self):
        self._test_has_user_role_with(UserRoles.ADMIN, UserRoles.EXPERT, True)
    
    def test_has_user_role_returnsTrue_ifUserIsAdminAndTestForAdmin(self):
        self._test_has_user_role_with(UserRoles.ADMIN, UserRoles.ADMIN, True)
    
    def test_is_admin_returnsTrue_whenUserIsAdmin(self):
        setUp.setUpTestAdmin()

        response = User.query.get(1).is_admin()

        self.assertEqual(response, True)
    
    def test_is_admin_returnsFalse_whenUserIsUser(self):
        setUp.setUpTestUser()

        response = User.query.get(1).is_admin()

        self.assertEqual(response, False)
    
    def test_is_admin_returnsFalse_whenUserIsExpert(self):
        setUp.setUpTestExpert()

        response = User.query.get(1).is_admin()

        self.assertEqual(response, False)
    
    def test_verify_reset_password_token_returnsCorrectUser_whenCorrespondingToken(self):
        token = TestToken(2, "password_reset")
        setUp.setUpTestUser()
        setUp.setUpTestAdmin()
        user = User.query.get(1)
        
        # calling method on user 1, but token is associated with user 2 
        # so we expect user 2 to be returned 
        response = user.verify_reset_password_token(token)
        
        self.assertEqual(response, User.query.get(2))
    
    def test_verify_reset_password_token_returnsNone_whenNoCorrespondingToken(self):
        token = TestToken(777, "password_reset")
        setUp.setUpTestUser()
        user = User.query.get(1)
        
        response = user.verify_reset_password_token(token)
        
        self.assertEqual(response, None)
    
    def test_verify_reset_password_token_returnsNone_whenTokenActionNotReset(self):
        token = TestToken(1, "do_nothing")
        setUp.setUpTestUser()
        user = User.query.get(1)
        
        response = user.verify_reset_password_token(token)
        
        self.assertEqual(response, None)

    def test_load_user_returnsCorrectUser_whenValidUsersInDb(self):
        setUp.setUpTestUser()
        setUp.setUpTestAdmin()

        response_one = load_user(1)
        response_two = load_user(2)

        self.assertEqual(response_one, User.query.get(1))
        self.assertEqual(response_two, User.query.get(2))
    
    def test_load_user_returnsNone_whenUserNotInDb(self):

        response_one = load_user(1)

        self.assertEqual(response_one, None)




    # helper methods
    ############################################################################
    def _test_has_user_role_with(self, actualUserRole, testUserRole, expectedOutcome):
        user = User()
        data=dict(email="user@email.com", password="password", name="name")
        user.from_dict(data, new_user=True)
        user.user_role = actualUserRole

        response = user.has_user_role(testUserRole)

        self.assertEqual(response, expectedOutcome)


if __name__ == "__main__":
    unittest.main()