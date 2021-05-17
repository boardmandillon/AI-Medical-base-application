import click
import json

from app.commands import ml_bp
from app.commands.cli_admin import login
from app.projects.aap_diagnosis.aap_diagnosis_model import \
    AAPDiagnosisModel, AAPMenDiagnosisModel, AAPWomenDiagnosisModel, AAPGynDiagnosisModel


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
            
            count=0 # to keep track of where in the data we are
            # split data into 70% training data and 30% test data, and save
            training_limit = 0.7 * len(data)    

            for i, symptoms in enumerate(data):
                diagnosis = model(user_id=user.id)
                label = diagnosis.get_label_from_numeric(labels[i])
                diagnosis.ml_symptoms = symptoms
                if count<training_limit:
                    diagnosis.l_actual_diagnosis = label
                    count+=1
                else:
                    diagnosis.te_l_actual_diagnosis = label
                

                diagnosis.save()

            print("{} data records added".format(i))
            print("{} set aside for training, {} set aside for testing".format(count, len(data)-count))
            return True
    else:
        print("User must sign in as an admin to perform this function")
        return


@ml_bp.cli.command('load_aap_data')
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

@ml_bp.cli.command('load_aap_men_data')
@click.argument('json_file')
def train(json_file):
    """Loads AAP Men training data from the given JSON file and saves it
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
    load_data(json_file, AAPMenDiagnosisModel)

@ml_bp.cli.command('load_aap_women_data')
@click.argument('json_file')
def train(json_file):
    """Loads AAP Women training data from the given JSON file and saves it
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
    load_data(json_file, AAPWomenDiagnosisModel)


@ml_bp.cli.command('load_aap_gyn_data')
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
