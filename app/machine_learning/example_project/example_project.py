import datetime
import json

from app.models.projects.example_model import ExampleModel
from app.machine_learning.decision_tree import DecisionTree
from app import celery


class ExampleProject:
    """Example AI class to use when defining your own."""

    project_name = None
    classifier = None

    # All possible labels and corresponding unique numerical identifiers
    labels = {
        'mammal': 0,
        'reptile': 1,
    }

    def __init__(self):
        """Initialise project class and classifier."""

        self.project_name = self.__class__.__name__
        self.classifier = DecisionTree(
            self.project_name, ExampleModel, self.labels)

    def _save_data(self, data, current_user):
        """Save the passed in data to Mongo."""

        print("{} | Saving a new model with the data: {}".format(
            self.project_name, data))

        model = ExampleModel(user_id=current_user.id, **data)
        model.save()

        return model

    def _update_prediction(self, doc_id, prediction):
        """Update the document with the new prediction."""

        print("{} | Updating document '{}' with prediction: '{}'".format(
            self.project_name, doc_id, prediction))

        model = ExampleModel.objects.get(id=doc_id).update(
            set__actual_species=prediction,
            set__date_modified=datetime.datetime.utcnow(),
        )

        print("{} | Document '{}' has been updated".format(
            self.project_name, doc_id))

        return model

    # @celery.task
    def _make_prediction(self, doc_id, data):
        """Calculate the prediction from the classifier and update the
        stored prediction for the document with the given id.
        """
        prediction = self.classifier.predict(data)
        self._update_prediction(doc_id, prediction)

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
        # self._make_prediction.delay(model.id, data)
        self._make_prediction(model.id, json.loads(model.to_json()))

        return model
