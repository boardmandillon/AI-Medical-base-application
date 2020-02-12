from rq import get_current_job

import time

from app import create_app

app = create_app()
app.app_context().push()


def train_aap_diagnosis():
    """Task for training the AI of the AAP diagnosis project."""
    job = get_current_job()

    # Should probably include a check to see if the model actually needs
    # training
    print("Training...")

    # Could add some sort of progress updates
    # job.meta['progress'] = 100.0 * i / seconds
    # job.save_meta()

    return


def example(seconds):
    """Example Redis task."""
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')
