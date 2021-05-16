from flask import current_app as app

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
    labels = None  # Possible labels for the data
    ml_model_date_modified = None  # Database ID of the current ML model
    ml_model = None  # Current machine learning model being used
    ml_data = None  # Data used for training fetched from the database
    ml_target = None  # ML target field from the database model
    ml_label = None  # Label field to use for training
    last_checked = None  # Date time of last ML model check

        # test data 
    te_ml_data = None # test data fetched from the database
    te_ml_target = None # test target field from the database model
    te_ml_label = None  # test label field for test data
    doc_ids = None


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
            app.logger.info(
                "{} | Updating the existing ML model: {}...".format(
                    self.project_name, doc_id))

            model = MLModel.objects(id=doc_id).get()
        else:
            app.logger.info("{} | Saving the new ML model...".format(
                self.project_name))

            model = MLModel()

        model.project_name = self.project_name
        model.training = training

        if ml_model:
            model.ml_model.put(pickle.dumps(ml_model))

        model.save()

        app.logger.info("{} | Model saved".format(self.project_name))

        return model

    def train(self, *args, **kwargs):
        """Function to be implemented by the specific machine learning
        algorithms.
        """
        raise NotImplementedError

    def _load_ml_model(self):
        """Load the latest machine learning model."""
        model = MLModel.objects.filter(
            project_name=self.project_name, training=False).order_by(
                '-id.generation_time').first()

        if model:
            if not self.ml_model or \
                    model.id.generation_time > self.ml_model_date_modified:

                app.logger.info(
                    "{} | New machine learning model found, loading...".format(
                        self.project_name))

                self.ml_model = pickle.loads(model.ml_model.read())
                self.ml_model_date_modified = model.id.generation_time

                app.logger.info("{} | Machine learning model loaded".format(
                    self.project_name))
        else:
            app.logger.warning(
                "{} | No machine learning models found in the the database"
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

        app.logger.info(
            "{} | Fetching training data from the database...".format(
                self.project_name))

        self.ml_data = json.loads(self.db_model.objects().to_json())

        app.logger.info("{} | Fetched all entries from the database".format(
            self.project_name))

    def _check_for_new_ml_model(self):
        """If enough time has passed (defined by HOURS_BETWEEN_CHECKS)
        the database will be checked for a newer machine learning model.
        If one exists it will be loaded.
        """
        delta = datetime.datetime.utcnow() - self.last_checked

        if delta.seconds > (self.HOURS_BETWEEN_CHECKS * 60 * 60):
            app.logger.info(
                "{} | {} hours has passed, checking for a new ML model..."
                "".format(self.project_name, self.HOURS_BETWEEN_CHECKS))

            self._load_ml_model()

    def _check_if_ml_model_is_already_training(self):
        """Checks and returns whether a machine learning model is currently
        being trained. If no models are found False is returned.
        """
        training = False

        model = MLModel.objects.filter(
            project_name=self.project_name).order_by(
                '-id.generation_time').first()

        if model:
            training = model.training
            app.logger.info(
                "{} | The latest machine learning model is training: {}"
                "".format(self.project_name, training))

        return training

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
        app.logger.info("{} | Preparing machine learning data...".format(
            self.project_name))

        # Create a shallow copy of the data
        if isinstance(data, dict):
            data = [dict(data)]
        elif isinstance(data, list):
            data = list(data)
        else:
            app.logger.error(
                "{} | Data to prepare is in an incorrect format, should be "
                "of type dict or list".format(self.project_name))
            return

        ml_data = []

        app.logger.info("{} | Deleting non 'ml_' and 'l_' fields...".format(
            self.project_name))

        for i in data:
            classified = False
            extra_fields = {}

            for f in list(i.keys()):
                if f.startswith('ml_'):
                    # Expand list fields into separate fields
                    if i[f] is not None and isinstance(i[f], list):
                        for index, value in enumerate(i[f]):
                            extra_fields[f + str(index)] = value
                        del i[f]
                else:
                    # Set target and label fields
                    if f.startswith('l_'):
                        # Fetch numeric label from string
                        i[f] = self.labels.get(i.get(f))

                        if i[f] is not None:
                            classified = True

                        if not self.ml_label:
                            self.ml_label = f

                            app.logger.info(
                                "{} | Found field '{}' starting with 'l_', "
                                "using this field as the label field".format(
                                    self.project_name, self.ml_label))
                    else:
                        if f.startswith('t_'):
                            if not self.ml_target:
                                self.ml_target = f

                                app.logger.info(
                                    "{} | Found field '{}' starting with 't_'"
                                    ", using this field as the target field"
                                    "".format(
                                        self.project_name, self.ml_target))

                        del i[f]

            # Only include data that has a label in the training data set
            if classified or not ignore_unclassified:
                if extra_fields:
                    i.update(extra_fields)
                ml_data.append(i)

        return ml_data, self.ml_label
    
    def prepare_test_data(self, data, ignore_unclassified=True):
        """Prepares the data for testing accuracy.

        * The first field found to start with "te_t_" will be treated as the
            target field unless one has already been identified. The target
            field is the field the machine learning prediction should be
            stored in. It will be deleted from the data.
        * The first field found to start with "te_l_" will be treated as the
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
        app.logger.info("{} | Preparing machine learning test data...".format(
            self.project_name))

        # Create a shallow copy of the data
        if isinstance(data, dict):
            data = [dict(data)]
        elif isinstance(data, list):
            data = list(data)
        else:
            app.logger.error(
                "{} | Data to prepare is in an incorrect format, should be "
                "of type dict or list".format(self.project_name))
            return

        te_ml_data = []
        doc_ids = []
        app.logger.info("{} | Deleting non 'ml_' and 'l_' fields...".format(
            self.project_name))

        for i in data:
            classified = False
            extra_fields = {}

            for f in list(i.keys()):
                if f.startswith('ml_'):
                    # Expand list fields into separate fields
                    if i[f] is not None and isinstance(i[f], list):
                        for index, value in enumerate(i[f]):
                            extra_fields[f + str(index)] = value
                        del i[f]
                else:
                    # don't delete doc_id
                    if f.startswith('_id'):
                        continue
                    # Set test target and test label fields
                    if f.startswith('te_l_'):
                        # Fetch numeric label from string
                        i[f] = self.labels.get(i.get(f))

                        if i[f] is not None:
                            classified = True

                        if not self.te_ml_label:
                            self.te_ml_label = f

                            app.logger.info(
                                "{} | Found field '{}' starting with 'l_', "
                                "using this field as the label field".format(
                                    self.project_name, self.te_ml_label))
                    else:
                        if f.startswith('te_t_'):
                            if not self.te_ml_target:
                                self.te_ml_target = f

                                app.logger.info(
                                    "{} | Found field '{}' starting with 't_'"
                                    ", using this field as the target field"
                                    "".format(
                                        self.project_name, self.te_ml_target))
                        else:
                            del i[f]

            # Only include data that has a label in the training data set
            if classified or not ignore_unclassified:
                if extra_fields:
                    i.update(extra_fields)
                te_ml_data.append(i)
                doc_ids.append(i['_id'])

        return te_ml_data, self.te_ml_label, doc_ids

