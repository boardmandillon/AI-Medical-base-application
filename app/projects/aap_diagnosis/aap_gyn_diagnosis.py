from flask import current_app as app

import json

from app.projects.aap_diagnosis.aap_diagnosis import AAPDiagnosis
from app.projects.aap_diagnosis.aap_diagnosis_model import AAPGynDiagnosisModel
from app.machine_learning.bernoulli_naive_bayes import BernoulliNaiveBayes
from app import celery


class AAPGynDiagnosis(AAPDiagnosis):
    """AAP diagnosis project for diagnosing acute abdominal pain with gynae."""

    PROJECT_NAME = "AAPGynDiagnosis"
    MODEL = AAPGynDiagnosisModel


@celery.task(name='aap_gyn_diagnosis_predict')
def make_prediction(doc_id, data):
    """Celery task to calculate the diagnosis prediction for the data.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.

    :type doc_id: str
    :type data: dict
    """
    classifier = BernoulliNaiveBayes(
        AAPGynDiagnosis.PROJECT_NAME, AAPGynDiagnosis.MODEL,
        AAPGynDiagnosis.MODEL.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        app.logger.info(
            "{} | Updating document '{}' with prediction: '{}'".format(
                AAPGynDiagnosis.PROJECT_NAME, doc_id, prediction))

        AAPGynDiagnosis.MODEL.objects.get(id=doc_id).update(
            set__t_diagnosis=prediction,
        )


@celery.task(name='aap_gyn_diagnosis_train')
def train_classifier(force_retrain=False):
    """Periodic Celery task for retraining the ML model if the data has
    changed.

    :param force_retrain: Whether to ignore if a model is already in the
        process of being trained, default is False.
    :type force_retrain: bool
    """
    classifier = BernoulliNaiveBayes(
        AAPGynDiagnosis.PROJECT_NAME, AAPGynDiagnosis.MODEL,
        AAPGynDiagnosis.MODEL.possible_labels)

    classifier.train(force_retrain=force_retrain)
