from app.models.project_base import ProjectBase
from app import db_mongo as db

from datetime import datetime


class skinCancerModel(ProjectBase):
    """Document definition for the skin cancer analysis project.
    Stores the image metadata including filename, upload date and content type.
    Image is stored in binary format using GridFS to divide the file into chunks"""

    possible_labels = {}

    content_type = db.StringField(required=False)
    diagnosis_photo = db.FileField(required=True)

    t_diagnosis = db.StringField()
    l_actual_diagnosis = db.StringField()
