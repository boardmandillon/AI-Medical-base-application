import click
import json

from app.commands import bp
from app.commands.helpers import login
from app.projects.aap_diagnosis.aap_diagnosis_model import \
    AAPDiagnosisModel, AAPGynDiagnosisModel


def load_data(json_file, model):
    """Loads training data from the JSON file and saves it in the database
    under the given model.

    Requires the user sign in as an admin.
    """
    user = login()
    if user:
        with open(json_file, "r") as f:
            contents = json.load(f)
            data = contents.get("data")
            labels = contents.get("labels")

            if not data or not labels or len(data) != len(labels):
                print("Please provide a file in the correct format")
                return

            for i, symptoms in enumerate(data):
                model = model()
                label = model.get_label_from_numeric(labels[i])
                model.user_id = user.id
                model.ml_symptoms = symptoms
                model.l_actual_diagnosis = label
                model.save()
            return True
    else:
        print("User must sign in as an admin to perform this function")
        return


@bp.cli.command('load_aap_data')
@click.argument('json_file')
def train(json_file):
    """Loads AAP training data from the given JSON file and saves it
    to the database.

    :param json_file: JSON file name, with the file it corresponds to being
        in the format:
        {
            "data": [
                [symptom1, symptom2, ..., symptomN],
                ...
            ],
            "labels": [
                label1, ...
            ]
        }
        Where the symptoms corresponds to 1 if the patient has that symptom
        or 0 if not. The label is a numerical value representing the class
        which the row is in.
    """
    load_data(json_file, AAPDiagnosisModel)


@bp.cli.command('load_aap_gyn_data')
@click.argument('json_file')
def train(json_file):
    """Loads AAP Gyn training data from the given JSON file and saves it
    to the database.

    :param json_file: JSON file name, with the file it corresponds to being
        in the format:
        {
            "data": [
                [symptom1, symptom2, ..., symptomN],
                ...
            ],
            "labels": [
                label1, ...
            ]
        }
        Where the symptoms corresponds to 1 if the patient has that symptom
        or 0 if not. The label is a numerical value representing the class
        which the row is in.
    """
    load_data(json_file, AAPGynDiagnosisModel)
