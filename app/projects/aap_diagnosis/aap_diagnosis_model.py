from app.models.project_base import ProjectBase
from app import db_mongo as db


class AAPDiagnosisModel(ProjectBase):
    """Document definition for AAP diagnosis."""
    possible_labels = {}

    # ml_

    t_diagnosis = db.ListField(db.StringField())
    l_actual_diagnosis = db.StringField()
