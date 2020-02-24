from datetime import datetime
import json

from app.models.projects.example_model import ExampleModel
from app.machine_learning.decision_tree import DecisionTree
from app import celery

PROJECT_NAME = "ExampleProject"
LABELS = {
    'mammal': 0,
    'reptile': 1,
}


class ExampleProject:
    """Example AI class to use when defining your own."""

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB."""

        print("{} | Saving a new model with the data: {}".format(
            PROJECT_NAME, data))

        model = ExampleModel(user_id=current_user.id, **data)
        model.save()

        return model

    @staticmethod
    def predict(data, current_user):
        """Performs the following tasks:

        1. Save the passed in data as a document in MongoDB.

        The next steps are done in parallel:
        2a. Return the document model.

        2b. Calculate the prediction from the classifier.
        3b. Update the stored prediction for the document.

        :param data: Data to use for prediction.
        :param current_user: The user model to save the document under.
        :type data: dict
        :type current_user: User

        :return: The document model representing the data, without
            the prediction
        :rtype: ExampleModel
        """
        model = ExampleProject._save_data(data, current_user)

        # Make predictions asynchronously
        make_prediction.delay(
            str(model.id), model.to_json())

        return model


@celery.task
def make_prediction(doc_id, data):
    """Celery task to calculate the prediction for the data from the
    classifier and update the stored prediction for the document with
    the given id.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.

    :type doc_id: str
    :type data: dict
    """
    classifier = DecisionTree(
        PROJECT_NAME, ExampleModel, LABELS)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        print("{} | Updating document '{}' with prediction: '{}'".format(
            PROJECT_NAME, doc_id, prediction))

        ExampleModel.objects.get(id=doc_id).update(
            set__t_species=prediction,
            set__date_modified=datetime.utcnow(),
        )


@celery.task(name='example_project_train')
def train_classifier():
    """"Periodic Celery task for retraining the ML model if the data has
    changed.
    """
    classifier = DecisionTree(PROJECT_NAME, ExampleModel, LABELS)
    classifier.train()
