from app.models.projects.project_base import ProjectBase
from app import db_mongo as db


class UrineDipstickAnalysis(ProjectBase):
    """Document definition for the urine dipstick analysis project."""
    actual_diagnosis = db.StringField()
