import json

from app.models.project_base import ProjectBase
from app import db_mongo as db
from .aap_questions import AAP_QUESTIONS, AAP_GYN_QUESTIONS


class AAPBaseModel(ProjectBase):
    """Base document model for the AAP and AAP gyn models."""
    possible_labels = {}
    number_symptoms = None
    questions = None
    t_diagnosis = None
    l_actual_diagnosis = None

    ml_symptoms = db.ListField(db.IntField(), required=True)

    # test data 
    te_t_diagnosis = None # test target field from the database model
    te_l_actual_diagnosis = None  # test label field for test data

    meta = {'allow_inheritance': True}

    def from_dict(self, data):
        """Take the given dict and set the numerical values of the model
        from it.

        :param data: The dict to get the numerical data from.
        :raises ValueError: If the given data is invalid.
        """
        symptoms = [0] * self.number_symptoms

        # Init arrays for errors
        missing_fields = []
        too_many_answers_fields = []
        invalid_answers = []

        for q in self.questions:
            received_answers = data.get(q, [])
            answers = self.questions[q].get("answers")
            required = self.questions[q].get("required")
            mutually_exclusive = self.questions[q].get("mutually_exclusive")

            if required and not received_answers:
                missing_fields.append(q)
                continue
            elif mutually_exclusive and len(received_answers) > 1:
                too_many_answers_fields.append(q)
                continue

            for a in received_answers:
                a = a.lower().strip()
                if a not in answers:
                    invalid_answers.append("{} = {}".format(q, a))
                    continue
                else:
                    symptoms[answers[a] - 1] = 1

        if missing_fields:
            raise ValueError(
                "The following questions must be answered: {}".format(
                    ", ".join(missing_fields)))
        if too_many_answers_fields:
            raise ValueError(
                "Only one answer must be provided to the following fields: "
                "{}".format(", ".join(too_many_answers_fields)))
        if invalid_answers:
            raise ValueError(
                "The following fields and answers are invalid: {}".format(
                    ", ".join(invalid_answers)))

        self.ml_symptoms = symptoms

    def to_dict(self):
        """Return a dict containing the questions and answers of the
        diagnosis from the stored numeric values.
        """
        questions = {"answers": {}}
        for i, value in enumerate(self.ml_symptoms):
            if value:
                for q in self.questions:
                    answers = self.questions[q]["answers"]
                    for a in answers:
                        if answers[a] == i + 1:
                            if not questions["answers"].get(q):
                                questions["answers"][q] = [a]
                            else:
                                questions["answers"][q].append(a)

        questions.update(json.loads(self.to_json()))
        return questions

    def set_actual_diagnosis(self, actual_diagnosis):
        """Set the actual diagnosis field to confirm the real diagnosis.

        :param actual_diagnosis: Actual diagnosis.
        :type actual_diagnosis: str

        :return: True if the disease exists, else False.
        :rtype: bool
        """
        for i in self.possible_labels.keys():
            if actual_diagnosis.lower() == i.lower():
                self.l_actual_diagnosis = i
                return True
        return False


class AAPDiagnosisModel(AAPBaseModel):
    """Document definition for AAP diagnosis."""
    possible_labels = {
        "Appendicitis": 1,
        "Diverticular Disease": 2,
        "Perforated Ulcer": 3,
        "Non Specific Abdominal Pain": 4,
        "Cholecystitis": 5,
        "Bowel Obstruction": 6,
        "Pancreatitis": 7,
        "Renal Colic": 8,
        "Dyspepsia": 9,
    }
    number_symptoms = 136
    questions = AAP_QUESTIONS

    t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    te_t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    te_l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    
class AAPMenDiagnosisModel(AAPBaseModel):
    """Document definition for Men AAP diagnosis."""
    possible_labels = {
        "Appendicitis": 1,
        "Diverticular Disease": 2,
        "Perforated Ulcer": 3,
        "Non Specific Abdominal Pain": 4,
        "Cholecystitis": 5,
        "Bowel Obstruction": 6,
        "Pancreatitis": 7,
        "Renal Colic": 8,
        "Dyspepsia": 9,
    }
    number_symptoms = 136
    questions = AAP_QUESTIONS

    aap_id = db.StringField(null=True)
    t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    te_t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    te_l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    
    def setAapId(self, aap_id):
        self.aap_id = aap_id

class AAPWomenDiagnosisModel(AAPBaseModel):
    """Document definition for Women AAP diagnosis."""
    possible_labels = {
        "Appendicitis": 1,
        "Diverticular Disease": 2,
        "Perforated Ulcer": 3,
        "Non Specific Abdominal Pain": 4,
        "Cholecystitis": 5,
        "Bowel Obstruction": 6,
        "Pancreatitis": 7,
        "Renal Colic": 8,
        "Dyspepsia": 9,
    }
    number_symptoms = 136
    questions = AAP_QUESTIONS

    aap_id = db.StringField(null=True)
    t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    te_t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    te_l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    
    def setAapId(self, aap_id):
        self.aap_id = aap_id

class AAPGynDiagnosisModel(AAPBaseModel):
    """Document definition for AAP diagnosis with additional gynae fields."""
    possible_labels = {
        "Appendicitis": 1,
        "Non Specific Abdominal Pain": 2,
        "Urinary Tract Infection": 3,
        "Pelvic Inflammatory Disease": 4,
        "Ovarian Cyst": 5,
        "Ectopic Pregnancy": 6,
        "Incomplete Abortion": 7,
    }
    number_symptoms = 157
    questions = AAP_GYN_QUESTIONS

    t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    te_t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
    te_l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)

