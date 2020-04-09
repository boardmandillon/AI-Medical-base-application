from app.models.project_base import ProjectBase
from app import db_mongo as db

from datetime import datetime


class UrineDipstickModel(ProjectBase):
    """Document definition for the urine dipstick analysis project.
    Stores the image metadata including filename, upload date and content type.
    Image is stored in binary format using GridFS to divide the file into chunks"""

    possible_labels = {}

    filename = db.StringField(required=True)
    upload_date = db.DateTimeField(default=datetime.utcnow())
    content_type = db.StringField(required=True)
    diagnosis_photo = db.FileField(required=True)

    t_diagnosis = db.ListField(db.StringField())
    l_actual_diagnosis = db.StringField()
