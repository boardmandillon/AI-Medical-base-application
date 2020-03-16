from app import db_mongo as db


class ProjectBase(db.Document):
    """Base document schema definition for Vulture individual projects.

    Inherit from this class when defining your own project Document classes.

    The following fields must be included:
    * Target field: This is the field which the machine learning algorithm will
        save it's prediction/output to. It should be denoted by appending
        't_' to its field name.
    * Label field: The supervised machine learning algorithms will use this
        field for training. It should be denoted by appending 'l_' to its
        field name.
    * Data fields: Fields containing information to make a prediction from.
        They should be denoted by appending 'ml_' to their field names.
    """
    user_id = db.IntField(required=True)

    # Automatically created fields
    index = db.IntField()

    meta = {
        'collection': 'projects',
        'allow_inheritance': True,
        'indexes': [
            'index',
        ],
        'auto_create_index': True,
        'ordering': ['-id.generation_time'],
    }
