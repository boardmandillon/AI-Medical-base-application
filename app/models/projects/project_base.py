from app import db_mongo as db


class ProjectBase(db.Document):
    """Base document schema definition for Vulture individual projects."""
    user_id = db.IntField(required=True)
    project_id = db.IntField()

    meta = {
        'collection': 'projects',
        'allow_inheritance': True,
    }
