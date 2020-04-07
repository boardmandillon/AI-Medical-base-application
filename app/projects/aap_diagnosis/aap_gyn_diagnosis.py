import json

from app.projects.aap_diagnosis.aap_diagnosis import AAPDiagnosis
from app.projects.aap_diagnosis.aap_diagnosis_model import AAPGynDiagnosisModel
from app.machine_learning.gaussian_naive_bayes import GaussianNaiveBayes
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
    classifier = GaussianNaiveBayes(
        AAPGynDiagnosis.PROJECT_NAME, AAPGynDiagnosis.MODEL,
        AAPGynDiagnosis.MODEL.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        print("{} | Updating document '{}' with prediction: '{}'".format(
            AAPGynDiagnosis.PROJECT_NAME, doc_id, prediction))

        AAPGynDiagnosis.MODEL.objects.get(id=doc_id).update(
            set__t_diagnosis=prediction,
        )


@celery.task(name='aap_gyn_diagnosis_train')
def train_classifier():
    """Periodic Celery task for retraining the ML model if the data has
    changed.
    """
    classifier = GaussianNaiveBayes(
        AAPGynDiagnosis.PROJECT_NAME, AAPGynDiagnosis.MODEL,
        AAPGynDiagnosis.MODEL.possible_labels)

    classifier.train()
