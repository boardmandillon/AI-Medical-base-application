from app.models.projects.project_base import ProjectBase
from app import db_mongo as db


class AAPDiagnosis(ProjectBase):
    """Document definition for AAP diagnosis."""
    diagnoses = db.ListField(db.StringField())
    actual_diagnosis = db.StringField()
