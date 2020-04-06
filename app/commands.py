from flask import Blueprint

import click
from getpass import getpass

from app import celery, db_relational as db
from config import Config
from app.models.user import User, UserRoles

ml = Blueprint('ml', __name__)
cli_admin = Blueprint('cli_admin', __name__)


@ml.cli.command('train')
@click.argument('project_train_task')
def train(project_train_task):
    """Trains the machine learning model using the celery task name.

    :param project_train_task: Celery task name for training the machine
        learning model of the project.
    """
    # Celery task must be define in the Celery beat schedule
    if project_train_task in Config.CELERYBEAT_SCHEDULE:
        print("Executing the celery task '{}' in parallel".format(
            project_train_task))
        celery.send_task(project_train_task)
    else:
        print("'{}' is not a valid celery task name for training a machine"
              "learning model".format(project_train_task))


@cli_admin.cli.command('createsuperuser')
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
        print('Must include email, password, name and date of '
              'birth fields')
    elif User.query.filter_by(email=data.get("email")).first():
        print('please use a different email address')
    else:
        user = User()
        user.from_dict(data, new_user=True)
        user.user_role = UserRoles.ADMIN
        db.session.add(user)
        db.session.commit()
