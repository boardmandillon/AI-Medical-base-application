from flask import current_app as app

import json

from app.projects.aap_diagnosis.aap_diagnosis_model import AAPDiagnosisModel
from app.machine_learning.bernoulli_naive_bayes import BernoulliNaiveBayes
from app import celery


class AAPDiagnosis:
    """AAP diagnosis project for diagnosing acute abdominal pain."""

    PROJECT_NAME = "AAPDiagnosis"
    MODEL = AAPDiagnosisModel

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB under the given user.

        :return: Returns the model saved and an error message if there is one.
            If an error occurs the None will be returned as the model.
        :rtype: AAPDiagnosisModel, None or None, str
        """

        app.logger.info("{} | Saving a new model with the data: {}".format(
            AAPDiagnosis.PROJECT_NAME, data))

        model = AAPDiagnosis.MODEL(user_id=current_user['id'])
        try:
            model.from_dict(data)
        except ValueError as e:
            return None, str(e)
        model.save()

        return model, None

    @staticmethod
    def predict(data, current_user):
        """Calculate diagnosis prediction from the given data.

        :param data: Data to use for prediction.
        :param current_user: The user model to save the document under.
        :type data: dict
        :type current_user: User

        :return: The document model representing the data, without the
            prediction and an error message if there is one. If an error
            occurs the None will be returned as the model.
        :rtype: AAPDiagnosisModel, None or None, str
        """
        model, error = AAPDiagnosis._save_data(data, current_user)

        if model and not error:
            make_prediction.delay(
                str(model.id), model.to_json())

        return model, error


@celery.task(name='aap_diagnosis_predict')
def make_prediction(doc_id, data):
    """Celery task to calculate the diagnosis prediction for the data.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.

    :type doc_id: str
    :type data: dict
    """
    classifier = BernoulliNaiveBayes(
        AAPDiagnosis.PROJECT_NAME, AAPDiagnosis.MODEL,
        AAPDiagnosis.MODEL.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        app.logger.info(
            "{} | Updating document '{}' with prediction: '{}'".format(
                AAPDiagnosis.PROJECT_NAME, doc_id, prediction))

        AAPDiagnosis.MODEL.objects.get(id=doc_id).update(
            set__t_diagnosis=prediction,
        )


@celery.task(name='aap_diagnosis_train')
def train_classifier(force_retrain=False):
    """Periodic Celery task for retraining the ML model if the data has
    changed.

    :param force_retrain: Whether to ignore if a model is already in the
        process of being trained, default is False.
    :type force_retrain: bool
    """
    classifier = BernoulliNaiveBayes(
        AAPDiagnosis.PROJECT_NAME, AAPDiagnosis.MODEL,
        AAPDiagnosis.MODEL.possible_labels)

    classifier.train(force_retrain=force_retrain)
