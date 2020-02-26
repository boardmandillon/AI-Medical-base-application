from app import db_mongo as db


class MLModel(db.Document):
    """Document for storing a pickled machine learning model."""
    project_name = db.StringField()
    ml_model = db.FileField()
    training = db.BooleanField(default=False)
