from getpass import getpass

from app.commands import cli_admin_bp as bp
from app.models.user import User, UserRoles
from app import db_relational as db


@bp.cli.command('createsuperuser')
def create_superuser():
    data = {
        "name": input("Name: "),
        "email": input("Email: "),
        "password": getpass(),
    }
    password2 = getpass(prompt='Confirm password: ')

    if data.get("password") != password2:
        print("Passwords are not the same")
    elif not (data.get("name") and data.get("email") and data.get("password")):
        print('Must include email, password and name fields')
    elif User.query.filter_by(email=data.get("email")).first():
        print('please use a different email address')
    else:
        user = User()
        user.from_dict(data, new_user=True)
        user.user_role = UserRoles.ADMIN
        db.session.add(user)
        db.session.commit()

def login():
    """Login an admin user.

    User must enter their email and password.

    :return: User object if login was successful, otherwise None.
    """
    data = {
        "email": input("Email: "),
        "password": getpass(),
    }

    if not (data.get("email") and data.get("password")):
        print('Please enter your Admin email and password')
        return

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]) or \
            not user.is_admin():
        print("Please enter a valid admin email and password")
        return
    else:
        return user
