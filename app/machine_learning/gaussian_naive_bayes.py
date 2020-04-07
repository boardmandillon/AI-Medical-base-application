from sklearn.naive_bayes import GaussianNB
# from sklearn import preprocessing
import pandas as pd

from app.machine_learning.ml_base.ml_base import MLBase

# TODO: Add prior weights properly
from app.projects.aap_diagnosis.aap_initial_weights import AAP_WEIGHTS


class GaussianNaiveBayes(MLBase):
    """Gaussian Naive Bayes classifier for use in projects."""

    priors = None

    def __init__(self, project_name, db_model, labels, priors=None):
        """Initiate a Gaussian Naive Bayes classifier.

        :param project_name: The name of the project.
        :param db_model: The database model class which the project uses.
        :param labels: A dictionary of numeric labels corresponding to their
            meanings.
        :param priors: Prior probabilities of the classes, default is None.

        :type project_name: str
        :type db_model: subclass(MLModel)
        :type labels: dict{int: obj}
        :type priors: list(int)
        """
        # TODO: Add prior weights properly
        self.priors = AAP_WEIGHTS
        super(GaussianNaiveBayes, self).__init__(
            project_name, db_model, labels)

    def train(self):
        """Train the Gaussian Naive Bayes classifier.

        The data needs to be prepared, normalised and separated first.
        After the training is complete the model is saved to MongoDB.
        """
        # Check if there is already a classifier being trained
        if not self._check_if_ml_model_is_already_training():
            print("{} | Training Gaussian Naive Bayes classifier...".format(
                self.project_name))

            if not self.ml_model:
                self.ml_model = GaussianNB(priors=self.priors)

            self.fetch_data()
            # le = preprocessing.LabelEncoder()
            # # Convert string labels into numbers.
            # wheather_encoded = le.fit_transform(wheather)
            data, label_field = self.prepare_data(self.ml_data)

            if not data and self.priors is None:
                print(
                    "{} | No data found for training and no prior weights "
                    "were given for the ML algorithm".format(
                        self.project_name))
            else:
                model = self._save_ml_model(training=True)

                if data:
                    # Normalise the data and separate the target field
                    data = pd.json_normalize(data)
                    ml_data = data.drop(label_field, axis=1)
                    label_values = data[label_field]

                    print("{} | Fitting model...".format(self.project_name))

                    self.ml_model.partial_fit(ml_data, label_values)

                    print("{} | Model fitted".format(self.project_name))
                else:
                    print("{} | No data found to train the ML algorithm, "
                          "using prior weights".format(self.project_name))

                self._save_ml_model(doc_id=model.id, ml_model=self.ml_model)
        else:
            print("{} | A Gaussian Naive Bayes classifier is already in the "
                  "process of being trained".format(self.project_name))

    def predict(self, data):
        """Returns the prediction of the Gaussian Naive Bayes classifier from
        the passed in data.

        :param data: Data to use for the prediction.
        :type data: dict

        :return: Target field prediction.
        """
        self._check_for_new_ml_model()

        if not self.ml_model:
            raise EnvironmentError(
                'No machine learning models found for project: {}'.format(
                    self.project_name))

        data, label_field = self.prepare_data(
            data, ignore_unclassified=False)

        if not data:
            print("{} | No data valid data found to make a prediction".format(
                self.project_name))

        # Normalise the data and separate the target field
        data = pd.json_normalize(data)
        ml_data = data.drop(label_field, axis=1)

        prediction = self.ml_model.predict(ml_data)

        # Retrieve the label from the numeric prediction value
        for label, numeric_label in self.labels.items():
            if numeric_label == prediction:
                return label
