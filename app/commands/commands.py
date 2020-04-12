import click

from app.commands import bp
from app import celery
from config import Config


@bp.cli.command('train')
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
        print("'{}' is not a valid celery task name for training a machine "
              "learning model".format(project_train_task))
