from getpass import getpass

from app.models.user import User


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
