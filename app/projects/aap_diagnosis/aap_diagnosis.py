import json

from app.projects.aap_diagnosis.aap_diagnosis_model import AAPDiagnosisModel
from app.machine_learning.gaussian_naive_bayes import GaussianNaiveBayes
from app import celery


class AAPDiagnosis:
    """AAP diagnosis project for diagnosing acute abdominal pain."""

    PROJECT_NAME = "AAPDiagnosis"
    MODEL = AAPDiagnosisModel

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB."""

        print("{} | Saving a new model with the data: {}".format(
            AAPDiagnosis.PROJECT_NAME, data))

        model = AAPDiagnosis.MODEL(user_id=current_user.id, **data)
        model.save()

        return model

    @staticmethod
    def predict(data, current_user):
        """Calculate diagnosis prediction from the given data.

        :param data: Data to use for prediction.
        :param current_user: The user model to save the document under.
        :type data: dict
        :type current_user: User

        :return: The document model representing the data, without
            the prediction
        :rtype: AAPDiagnosisModel
        """
        model = AAPDiagnosis._save_data(data, current_user)

        # Make predictions asynchronously
        make_prediction.delay(
            str(model.id), model.to_json())

        return model


@celery.task(name='aap_diagnosis_predict')
def make_prediction(doc_id, data):
    """Celery task to calculate the diagnosis prediction for the data.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.

    :type doc_id: str
    :type data: dict
    """
    classifier = GaussianNaiveBayes(
        AAPDiagnosis.PROJECT_NAME, AAPDiagnosis.MODEL,
        AAPDiagnosis.MODEL.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        print("{} | Updating document '{}' with prediction: '{}'".format(
            AAPDiagnosis.PROJECT_NAME, doc_id, prediction))

        AAPDiagnosis.MODEL.objects.get(id=doc_id).update(
            set__t_diagnosis=prediction,
        )


@celery.task(name='aap_diagnosis_train')
def train_classifier():
    """Periodic Celery task for retraining the ML model if the data has
    changed.
    """
    classifier = GaussianNaiveBayes(
        AAPDiagnosis.PROJECT_NAME, AAPDiagnosis.MODEL,
        AAPDiagnosis.MODEL.possible_labels)

    classifier.train()
