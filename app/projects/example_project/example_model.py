from app.models.project_base import ProjectBase
from app import db_mongo as db


class ExampleModel(ProjectBase):
    """Document definition for the example project. Including the definition
    of all the possible labels, which the machine learning classifier might
    assign the data. The labels have a unique numeric value assigned to them
    for use in training as the classifier can only use numeric labels.
    """
    possible_labels = {
        'mammal': 0,
        'reptile': 1,
    }

    ml_toothed = db.BooleanField(required=True)
    ml_breathes = db.BooleanField(required=True)
    ml_legs = db.BooleanField(required=True)

    t_species = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_species = db.StringField(
        choices=possible_labels.keys(), null=True)
