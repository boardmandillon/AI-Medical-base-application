from app.models.project_base import ProjectBase
from app import db_mongo as db
import datetime


class POC_OCR_Model(ProjectBase):
    """Document definition for the example project. Including the definition
    of all the possible labels, which the machine learning classifier might
    assign the data. The labels have a unique numeric value assigned to them
    for use in training as the classifier can only use numeric labels.
    """
    possible_labels = {}

    time = db.StringField(required=True)
    systolic = db.StringField(required=True)
    diastolic = db.StringField(required=True)
    heartRate = db.StringField(required=True)


