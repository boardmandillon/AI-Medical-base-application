import datetime
import json

from app.models.projects.example_model import ExampleModel
from app.machine_learning.decision_tree import DecisionTree
from app import celery


class ExampleProject:
    """Example AI class to use when defining your own."""

    project_name = None

    # All possible labels and corresponding unique numerical identifiers
    labels = {
        'mammal': 0,
        'reptile': 1,
    }

    def __init__(self):
        """Initialise the example project class."""
        self.project_name = self.__class__.__name__

    def _save_data(self, data, current_user):
        """Save the passed in data to MongoDB."""

        print("{} | Saving a new model with the data: {}".format(
            self.project_name, data))

        model = ExampleModel(user_id=current_user.id, **data)
        model.save()

        return model

    def predict(self, data, current_user):
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
        model = self._save_data(data, current_user)

        # Make predictions asynchronously
        make_prediction.delay(
            str(model.id), model.to_json(), self.project_name, self.labels)

        return model


@celery.task
def make_prediction(doc_id, data, project_name, labels):
    """Celery task to be run in parallel to calculate the prediction for the
    data from the classifier and update the stored prediction for the
    document with the given id.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.
    :param project_name: Name of the current project, used in logging.
    :param labels: A dictionary of numeric labels corresponding to their
        meanings.

    :type doc_id: str
    :type data: dict
    :type project_name: str
    :type labels: dict
    """
    classifier = DecisionTree(
        project_name, ExampleModel, labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        print("{} | Updating document '{}' with prediction: '{}'".format(
            project_name, doc_id, prediction))

        ExampleModel.objects.get(id=doc_id).update(
            set__t_species=prediction,
            set__date_modified=datetime.datetime.utcnow(),
        )
