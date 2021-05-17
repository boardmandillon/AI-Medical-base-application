from flask import current_app as app

import json
import pandas as pd

from app.projects.aap_diagnosis.aap_diagnosis_model import AAPMenDiagnosisModel
from app.machine_learning.bernoulli_naive_bayes import BernoulliNaiveBayes
from .aap_questions import AAP_QUESTIONS
from app import celery

from sklearn.metrics import accuracy_score

class AAPMenDiagnosis:
    """AAP diagnosis project for diagnosing acute abdominal pain.
        Used for the all men dataset."""

    PROJECT_NAME = "AAPMenDiagnosis"
    MODEL = AAPMenDiagnosisModel

    @staticmethod
    def _save_data(data, current_user, aap_id):
        """Save the passed in data to MongoDB under the given user.

        :return: Returns the model saved and an error message if there is one.
            If an error occurs the None will be returned as the model.
        :rtype: AAPMenDiagnosisModel, None or None, str
        """

        app.logger.info("{} | Saving a new model with the data: {}".format(
            AAPMenDiagnosis.PROJECT_NAME, data))

        model = AAPMenDiagnosis.MODEL(user_id=current_user['id'])
        try:
            model.from_dict(data)
            model.setAapId(str(aap_id))
        except ValueError as e:
            return None, str(e)
        model.save()

        return model, None

    @staticmethod
    def predict(data, current_user, aap_id):
        """Calculate diagnosis prediction from the given data.

        :param data: Data to use for prediction.
        :param current_user: The user model to save the document under.
        :type data: dict
        :type current_user: User

        :return: The document model representing the data, without the
            prediction and an error message if there is one. If an error
            occurs the None will be returned as the model.
        :rtype: AAPMenDiagnosisModel, None or None, str
        """
        model, error = AAPMenDiagnosis._save_data(data, current_user, aap_id)

        if model and not error:
            make_prediction.delay(
                str(model.id), model.to_json())

        return model, error
    
    def model_accuracy():
        """Calculates the accuracy of the model using the test data.
        Returns the mean accuracy on the given test data and labels.

        In multi-label classification, this is the subset accuracy which is a 
        harsh metric since you require for each sample that each label set be 
        correctly predicted.
        :return: float score of mean accuracy of prediction of test data
        """

        classifier = BernoulliNaiveBayes(
            AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL,
            AAPMenDiagnosis.MODEL.possible_labels
        )

        classifier.fetch_data()
        data, label_field, doc_ids = classifier.prepare_test_data(classifier.ml_data)

        if not data:
            app.logger.info("{} | Model {} has no test data.".format(
                    AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL))
            return None
        else:

            # # # # # # # # # # # # METHOD 1 # # # # # # # # # # # # # # # # # # # # # # 
            # Calculates mean accuracy of `self.predict(ml_data)` wrt. `label_values`.  

            data = pd.json_normalize(data)
            ml_data = data.drop([label_field, '_id.$oid', 'te_t_diagnosis'], axis=1)
            # label_field is te_l_actual_diagnosis
            label_values = data[label_field]

            score = classifier.ml_model.score(ml_data, label_values, sample_weight=None)

            app.logger.info("{} | Model {} has method 1 accuracy of {}.".format(
                AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL, score))

            # # # # # # # # # # # # METHOD 2 # # # # # # # # # # # # # # # # # # # # # # 
            # this one uses the predicted diagnoses for test data made from the 
            # training data model
            # and compares them to the actual test data diagnoses
            # to calculate accuracy

            # convert symptoms from string to number
            if(data['te_t_diagnosis'][0]!=None):
                str_y_pred = data['te_t_diagnosis']
                y_pred = str_y_pred.apply(lambda x : AAPMenDiagnosis.MODEL.possible_labels[x])
                y_true = data[label_field]
                second_score = accuracy_score(y_true, y_pred)

                app.logger.info("{} | Model {} has method 2 accuracy of {}.".format(
                    AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL, second_score))
            else:
                app.logger.info("{} | Model {} Accuracy cannot be calculated by method 2 as aap_diagnosis_test has not been run.".format(
                    AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL))

            return score


@celery.task(name='aap_men_diagnosis_predict')
def make_prediction(doc_id, data):
    """Celery task to calculate the diagnosis prediction for the data.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.

    :type doc_id: str
    :type data: dict
    """
    classifier = BernoulliNaiveBayes(
        AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL,
        AAPMenDiagnosis.MODEL.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        app.logger.info(
            "{} | Updating document '{}' with prediction: '{}'".format(
                AAPMenDiagnosis.PROJECT_NAME, doc_id, prediction))

        AAPMenDiagnosis.MODEL.objects.get(id=doc_id).update(
            set__t_diagnosis=prediction,
        )


@celery.task(name='aap_men_diagnosis_train')
def train_classifier(force_retrain=False):
    """Periodic Celery task for retraining the ML model if the data has
    changed.

    :param force_retrain: Whether to ignore if a model is already in the
        process of being trained, default is False.
    :type force_retrain: bool
    """
    classifier = BernoulliNaiveBayes(
        AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL,
        AAPMenDiagnosis.MODEL.possible_labels)

    classifier.train(force_retrain=force_retrain)


@celery.task(name='aap_men_diagnosis_test')
def test_classifier():
    """Celery task for using the classifier to calculate predictions
        for the test data.
    """
    classifier = BernoulliNaiveBayes(
            AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL,
            AAPMenDiagnosis.MODEL.possible_labels
        )

    classifier.fetch_data()
    data, label_field, doc_ids = classifier.prepare_test_data(classifier.ml_data)

    if not data:
        app.logger.info("{} | Model {} has no test data.".format(
                    AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL))
        return None
    else:
        app.logger.info("{} | Model {} being validated using test data...".format(
                    AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL))
        # use the existing model to make predictions on all test data
        #  update each testing record with doc_id corresponding to data
        for i in range(0, len(doc_ids)):
            model = AAPMenDiagnosisModel.objects.get_or_404(
                    id=doc_ids[i]['$oid'], user_id=1)

            if model:
                make_test_prediction.delay(
                    str(model.id), model.to_json()
            )


@celery.task(name='aap_men_diagnosis_test_predict')
def make_test_prediction(doc_id, data):
    """Celery task to calculate the diagnosis prediction for the TEST data.

    :param doc_id: The ID of the MongoDB document.
    :param data: Data to be used for classifying.

    :type doc_id: str
    :type data: dict
    """
    classifier = BernoulliNaiveBayes(
        AAPMenDiagnosis.PROJECT_NAME, AAPMenDiagnosis.MODEL,
        AAPMenDiagnosis.MODEL.possible_labels)

    prediction = classifier.predict(json.loads(data))

    if prediction:
        print(
            "{} | Updating document '{}' with TEST prediction: '{}'".format(
                AAPMenDiagnosis.PROJECT_NAME, doc_id, prediction))

        AAPMenDiagnosis.MODEL.objects.get(id=doc_id).update(
            set__te_t_diagnosis=prediction,
        )


def format_test_record(record):
    # record currently looks like
    # eg {'te_l_actual_diagnosis': 1, 'ml_symptoms0': 1, 'ml_symptoms1': 0, 'ml_symptoms2': 1, 'ml_symptoms3': 0, 'ml_symptoms4': 0, 'ml_symptoms5': 0, 'ml_symptoms6': 0, 'ml_symptoms7': 0, 'ml_symptoms8': 0, 'ml_symptoms9': 0, 'ml_symptoms10': 0, 'ml_symptoms11': 0, 'ml_symptoms12': 0, 'ml_symptoms13': 0, 'ml_symptoms14': 0, 'ml_symptoms15': 0, 'ml_symptoms16': 0, 'ml_symptoms17': 0, 'ml_symptoms18': 0, 'ml_symptoms19': 0, 'ml_symptoms20': 0, 'ml_symptoms21': 0, 'ml_symptoms22': 0, 'ml_symptoms23': 0, 'ml_symptoms24': 0, 'ml_symptoms25': 0, 'ml_symptoms26': 0, 'ml_symptoms27': 0, 'ml_symptoms28': 1, 'ml_symptoms29': 0, 'ml_symptoms30': 0, 'ml_symptoms31': 0, 'ml_symptoms32': 0, 'ml_symptoms33': 0, 'ml_symptoms34': 0, 'ml_symptoms35': 0, 'ml_symptoms36': 0, 'ml_symptoms37': 0, 'ml_symptoms38': 0, 'ml_symptoms39': 0, 'ml_symptoms40': 0, 'ml_symptoms41': 1, 'ml_symptoms42': 0, 'ml_symptoms43': 1, 'ml_symptoms44': 0, 'ml_symptoms45': 0, 'ml_symptoms46': 0, 'ml_symptoms47': 0, 'ml_symptoms48': 0, 'ml_symptoms49': 0, 'ml_symptoms50': 1, 'ml_symptoms51': 0, 'ml_symptoms52': 0, 'ml_symptoms53': 0, 'ml_symptoms54': 1, 'ml_symptoms55': 0, 'ml_symptoms56': 0, 'ml_symptoms57': 0, 'ml_symptoms58': 0, 'ml_symptoms59': 0, 'ml_symptoms60': 1, 'ml_symptoms61': 0, 'ml_symptoms62': 0, 'ml_symptoms63': 1, 'ml_symptoms64': 1, 'ml_symptoms65': 0, 'ml_symptoms66': 1, 'ml_symptoms67': 0, 'ml_symptoms68': 1, 'ml_symptoms69': 0, 'ml_symptoms70': 0, 'ml_symptoms71': 1, 'ml_symptoms72': 0, 'ml_symptoms73': 1, 'ml_symptoms74': 0, 'ml_symptoms75': 0, 'ml_symptoms76': 1, 'ml_symptoms77': 0, 'ml_symptoms78': 0, 'ml_symptoms79': 1, 'ml_symptoms80': 0, 'ml_symptoms81': 0, 'ml_symptoms82': 0, 'ml_symptoms83': 0, 'ml_symptoms84': 0, 'ml_symptoms85': 1, 'ml_symptoms86': 1, 'ml_symptoms87': 0, 'ml_symptoms88': 1, 'ml_symptoms89': 0, 'ml_symptoms90': 0, 'ml_symptoms91': 0, 'ml_symptoms92': 1, 'ml_symptoms93': 0, 'ml_symptoms94': 0, 'ml_symptoms95': 1, 'ml_symptoms96': 0, 'ml_symptoms97': 0, 'ml_symptoms98': 1, 'ml_symptoms99': 0, 'ml_symptoms100': 0, 'ml_symptoms101': 0, 'ml_symptoms102': 1, 'ml_symptoms103': 0, 'ml_symptoms104': 1, 'ml_symptoms105': 0, 'ml_symptoms106': 0, 'ml_symptoms107': 0, 'ml_symptoms108': 0, 'ml_symptoms109': 0, 'ml_symptoms110': 1, 'ml_symptoms111': 0, 'ml_symptoms112': 0, 'ml_symptoms113': 0, 'ml_symptoms114': 0, 'ml_symptoms115': 0, 'ml_symptoms116': 0, 'ml_symptoms117': 0, 'ml_symptoms118': 1, 'ml_symptoms119': 0, 'ml_symptoms120': 0, 'ml_symptoms121': 1, 'ml_symptoms122': 0, 'ml_symptoms123': 1, 'ml_symptoms124': 0, 'ml_symptoms125': 1, 'ml_symptoms126': 0, 'ml_symptoms127': 1, 'ml_symptoms128': 0, 'ml_symptoms129': 0, 'ml_symptoms130': 0, 'ml_symptoms131': 0, 'ml_symptoms132': 0, 'ml_symptoms133': 0, 'ml_symptoms134': 0, 'ml_symptoms135': 1}
    # this is the wrong format for the predict function
    # below we correctly format it

    # create dict formatted_record with same keys as AAP_QUESTIONS and values as empty lists []
    empty_lists = [[] for i in range(len(AAP_QUESTIONS))]
    formatted_record = dict(zip(AAP_QUESTIONS.keys(), empty_lists))
    # eg {'sex': [], 'age': [], 'site of pain at onset': [], 'site of pain at present': [], 'aggravating factors': [], 'relieving factors': [], 'progress': [], 'duration': [], 'type': [], 'severity': [], 'nausea': [], 'vomiting': [], 'anorexia': [], 'previous indigestion': [], 'jaundice': [], 'bowels': [], 'micturition': [], 'previous similar pain': [], 'previous abdo surgery': [], 'drugs for abdo pain': [], 'mood': [], 'colour': [], 'abdo movement': [], 'scar': [], 'distension': [], 'site of tenderness': [], 'rebound': [], 'guarding': [], 'rigidity': [], 'mass': [], 'murphy': [], 'bowel': [], 'rectal tenderness': []}

    # ignore te_l_actual_diagnosis, get string values of all the keys in record with value 1 
    # extract number and +1 to all, store in list num_symptoms
    str_symptoms = [k for k, v in record.items() if (v==1 and ("ml" in k))]
    # eg ['ml_symptoms0', 'ml_symptoms2', 'ml_symptoms28', 'ml_symptoms41', 'ml_symptoms43', 'ml_symptoms50', 'ml_symptoms54', 'ml_symptoms60', 'ml_symptoms63', 'ml_symptoms64', 'ml_symptoms66', 'ml_symptoms68', 'ml_symptoms71', 'ml_symptoms73', 'ml_symptoms76', 'ml_symptoms79', 'ml_symptoms85', 'ml_symptoms86', 'ml_symptoms88', 'ml_symptoms92', 'ml_symptoms95', 'ml_symptoms98', 'ml_symptoms102', 'ml_symptoms104', 'ml_symptoms110', 'ml_symptoms118', 'ml_symptoms121', 'ml_symptoms123', 'ml_symptoms125', 'ml_symptoms127', 'ml_symptoms135']

    num_symptoms = [int(s.strip("ml_symptoms"))+1 for s in str_symptoms]
    # eg [1, 3, 29, 42, 44, 51, 55, 61, 64, 65, 67, 69, 72, 74, 77, 80, 86, 87, 89, 93, 96, 99, 103, 105, 111, 119, 122, 124, 126, 128, 136]

    # for each key in AAP_QUESTIONS, add correct answers value to formatted_record if it matches one of the symptom numbers
    for k in AAP_QUESTIONS.keys():
        for n in AAP_QUESTIONS[k]["answers"]:  
            if AAP_QUESTIONS[k]["answers"][n] in num_symptoms:
                formatted_record[k].append(n)

    # final formatted record looks like:
    # eg {'sex': ['male'], 'age': ['<10'], 'site of pain at onset': [], 'site of pain at present': ['lower half'], 'aggravating factors': ['none'], 'relieving factors': ['vomiting'], 'progress': ['worse'], 'duration': ['2-7 days'], 'type': ['colicky'], 'severity': ['severe'], 'nausea': ['yes'], 'vomiting': ['yes'], 'anorexia': ['yes'], 'previous indigestion': ['no'], 'jaundice': ['no'], 'bowels': ['diarrhoea'], 'micturition': ['normal'], 'previous similar pain': ['no'], 'previous abdo surgery': ['yes'], 'drugs for abdo pain': ['yes'], 'mood': ['anxious'], 'colour': ['flushed'], 'abdo movement': ['normal'], 'scar': ['no'], 'distension': ['no'], 'site of tenderness': ['lower half'], 'rebound': ['yes'], 'guarding': ['no'], 'rigidity': ['no'], 'mass': ['no'], 'murphy': ['negative'], 'bowel': [], 'rectal tenderness': ['none']}
    return formatted_record