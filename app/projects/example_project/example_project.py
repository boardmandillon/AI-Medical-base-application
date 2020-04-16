from flask import current_app as app

import json

from app.projects.example_project.example_model import ExampleModel
from app.machine_learning.decision_tree import DecisionTree
from app import celery


class ExampleProject:
    """Example machine learning project class to use when defining your own."""

    PROJECT_NAME = "ExampleProject"

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB."""

        app.logger.info(
            "{} | Saving a new model with the data: {}".format(
                ExampleProject.PROJECT_NAME, data))

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


@celery.task(name='example_project_predict')
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
        ExampleProject.PROJECT_NAME, ExampleModel,
        ExampleModel.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        app.logger.info(
            "{} | Updating document '{}' with prediction: '{}'".format(
                ExampleProject.PROJECT_NAME, doc_id, prediction))

        target_info = ""
    else:
        prediction = ""
        target_info = 'An error has occurred, unable to make a prediction'

    ExampleModel.objects.get(id=doc_id).update(
        set__t_species=prediction,
        set__target_info=target_info,
    )


@celery.task(name='example_project_train')
def train_classifier(force_retrain=False):
    """Periodic Celery task for retraining the ML model if the data has
    changed.

    :param force_retrain: Whether to ignore if a model is already in the
        process of being trained, default is False.
    :type force_retrain: bool
    """
    classifier = DecisionTree(
        ExampleProject.PROJECT_NAME, ExampleModel,
        ExampleModel.possible_labels)

    classifier.train(force_retrain=force_retrain)
