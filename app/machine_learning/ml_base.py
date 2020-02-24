import pickle
import datetime
import json

from app.models.ml_model import MLModel


class MLBase(object):
    """Abstract base AI class to inherit from when defining machine learning
     classes. Contains all generic helper functions.
     """

    HOURS_BETWEEN_CHECKS = 12

    project_name = None
    db_model = None  # Model in the database to use
    ml_model_date_modified = None  # Database ID of the current ML model
    ml_model = None  # Current machine learning model being used
    ml_data = None  # Data used for training fetched from the database
    ml_target = None  # ML target field from the database model
    ml_label = None  # Label field to use for training
    last_checked = None  # Date time of last ML model check

    def __init__(self, project_name, db_model, labels):
        """Initiate the machine learning base class.

        :param project_name: Name of the project, used in logging.
        :param db_model: DB model which the project uses.
        :param labels: A dictionary of numeric labels corresponding to their
            meanings.

        :type project_name: str
        :type db_model: subclass(MLModel)
        :type labels: dict{int: obj})
        """
        super(MLBase, self).__init__()

        self.project_name = project_name
        self.db_model = db_model
        self.labels = labels

        self._load_ml_model()

    def _save_ml_model(self, doc_id=None, ml_model=None, training=False):
        """Save the machine learning model to MongoDB as a binary file."""
        if doc_id:
            print("{} | Updating the existing ML model: {}...".format(
                self.project_name, doc_id))

            model = MLModel.objects(id=doc_id)
            model.date_modified = datetime.datetime.utcnow()
        else:
            print("{} | Saving the new ML model...".format(self.project_name))

            model = MLModel()

        model.project_name = self.project_name
        model.training = training

        if ml_model:
            model.ml_model.put(pickle.dumps(ml_model))
            model.save()

        return model

    def train(self, *args, **kwargs):
        """Function to be implemented by the specific machine learning
        algorithms.
        """
        raise NotImplementedError

    def _load_ml_model(self):
        """Load the latest machine learning model."""
        model = MLModel.objects.filter(
            project_name=self.project_name).order_by(
                '-date_modified').first()

        if model:
            if not self.ml_model or \
                    model.date_modified > self.ml_model_date_modified:

                print("{} | New machine learning model found, loading..."
                      "".format(self.project_name))

                self.ml_model = pickle.loads(model.ml_model.read())
                self.ml_model_date_modified = model.date_modified

                print("{} | Machine learning model loaded".format(
                    self.project_name))
        else:
            print("{} | No machine learning models found in the the database"
                  "".format(self.project_name))

            self.ml_model = None

        self.last_checked = datetime.datetime.utcnow()

    def predict(self, *args, **kwargs):
        """Function to be implemented by the specific machine learning
        algorithms.
        """
        raise NotImplementedError

    def fetch_data(self):
        """Fetch all training data for the project from the database."""

        print("{} | Fetching training data from the database...".format(
            self.project_name))

        self.ml_data = json.loads(self.db_model.objects().to_json())

        print("{} | Fetched all entries from the database".format(
            self.project_name))

    def _check_for_new_ml_model(self):
        """If enough time has passed (defined by HOURS_BETWEEN_CHECKS)
        the database will be checked for a newer machine learning model.
        If one exists it will be loaded.
        """
        delta = datetime.datetime.utcnow() - self.last_checked

        if delta.seconds > (self.HOURS_BETWEEN_CHECKS * 60 * 60):
            print("{} | {} hours has passed, checking for a new ML "
                  "model...".format(self.project_name,
                                    self.HOURS_BETWEEN_CHECKS))

            self._load_ml_model()

    def _check_if_ml_model_is_already_training(self):
        """Checks and returns whether a machine learning model is currently
        being trained.
        """
        model = MLModel.objects.filter(
            project_name=self.project_name).order_by('-date_modified').first()

        print("{} | The latest machine learning model is training: {}".format(
            self.project_name, model.training))

        return model.training

    def prepare_data(self, data, ignore_unclassified=True):
        """Prepares the data for training/predictions.

        * The first field found to start with "t_" will be treated as the
            target field unless one has already been identified. The target
            field is the field the machine learning prediction should be
            stored in. It will be deleted from the data.
        * The first field found to start with "l_" will be treated as the
            label field unless one has already been identified. This field
            will be used by the machine learning algorithm to learn against.
        * Fields starting with "ml_" are treated as the fields to train the
            machine learning algorithm.
        * All other fields will be deleted from the data.

        :param data: Data to prepare, if it is a dict it will be wrapped
            in a list.
        :param ignore_unclassified: Whether or not to removed unclassified
            data from the data set, default is True.
        :type data: list or dict
        :type ignore_unclassified: bool

        :return: The prepared data and the identified label field.
        :rtype: list, str
        """
        print("{} | Preparing machine learning data...".format(
            self.project_name))

        # Create a shallow copy of the data
        if isinstance(data, dict):
            data = [dict(data)]
        elif isinstance(data, list):
            data = list(data)
        else:
            raise ValueError(
                "{} | Data to prepare is in an incorrect format, should be "
                "of type dict or list".format(self.project_name))

        ml_data = []

        print("{} | Deleting non 'ml_' fields...".format(self.project_name))

        for i in data:
            classified = False

            for f in list(i.keys()):
                if not f.startswith('ml_'):
                    if f.startswith('l_'):
                        # Fetch numeric label from string
                        i[f] = self.labels.get(i.get(f))

                        if i[f] is not None:
                            classified = True

                        if not self.ml_label:
                            self.ml_label = f

                            print("{} | Found field '{}' starting with 'l_', "
                                  "using this field as the label field"
                                  "".format(self.project_name, self.ml_label))
                    else:
                        if f.startswith('t_'):
                            if not self.ml_target:
                                self.ml_target = f

                                print("{} | Found field '{}' starting with "
                                      "'t_', using this field as the target "
                                      "field".format(self.project_name,
                                                     self.ml_target))

                        del i[f]

            if classified or not ignore_unclassified:
                ml_data.append(i)

        return ml_data, self.ml_label
