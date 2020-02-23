import datetime

from app import db_mongo as db


class ProjectBase(db.Document):
    """Base document schema definition for Vulture individual projects."""
    user_id = db.IntField(required=True)
    project_id = db.IntField(required=True)

    # Automatically created fields
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)
    date_modified = db.DateTimeField(default=datetime.datetime.utcnow)
    index = db.IntField()

    meta = {
        'collection': 'projects',
        'allow_inheritance': True,
        'indexes': [
            'index',
        ],
        'auto_create_index': True,
        'ordering': ['-date_modified'],
    }
