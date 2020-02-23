import datetime

from app import db_mongo as db


class MLModel(db.Document):
    """Document for storing a pickled machine learning model."""
    project_name = db.StringField()
    date_modified = db.DateTimeField(default=datetime.datetime.utcnow)
    ml_model = db.FileField()
