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
    possible_labels = {}

    user_id = db.IntField(required=True)
    target_info = db.StringField()

    # Automatically created fields
    index = db.IntField()

    meta = {
        'allow_inheritance': True,
        'indexes': [
            'index',
        ],
        'auto_create_index': True,
        'ordering': ['-id.generation_time'],
    }

    def get_label_from_numeric(self, numeric_label):
        """Returns the string value of the label from the integer numeric
        value.
        """
        for label in self.possible_labels:
            if self.possible_labels[label] == numeric_label:
                return label

    def get_numeric_from_label(self, string_label):
        """Returns the numeric integer value of the label from the string
        value.
        """
        return self.possible_labels[string_label]
