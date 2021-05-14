from app.models.project_base import ProjectBase
from app import db_mongo as db
import datetime


class POC_OCR_Model(ProjectBase):
    """Document definition for the Point of Care OCR project.
        Stores the results from a point of care device (Blood pressure monitor).
        Including time of the test, systolic value, diastolic value and heart rate of user
    """

    possible_labels = {}
    time = db.StringField(required=True)
    systolic = db.StringField(required=True)
    diastolic = db.StringField(required=True)
    heartRate = db.StringField(required=True)


