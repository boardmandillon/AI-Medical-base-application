from sklearn.naive_bayes import BernoulliNB
import pandas as pd
from flask import current_app as app

from app.machine_learning.ml_base.ml_base import MLBase


class BernoulliNaiveBayes(MLBase):
    """Bernoulli Naive Bayes classifier for use in projects with binary data,
    for example a list of true/false values corresponding to a list of
    symptoms.
    """

    def __init__(self, project_name, db_model, labels):
        """Initiate a Bernoulli Naive Bayesian classifier.

        :param project_name: The name of the project.
        :param db_model: The database model class which the project uses.
        :param labels: A dictionary of numeric labels corresponding to their
            meanings.

        :type project_name: str
        :type db_model: subclass(MLModel)
        :type labels: dict{int: obj}
        """
        super(BernoulliNaiveBayes, self).__init__(
            project_name, db_model, labels)

    def train(self, force_retrain=False):
        """Train the Bernoulli Naive Bayes classifier.

        The data needs to be prepared, normalised and separated first.
        After the training is complete the model is saved to MongoDB.

        :param force_retrain: Whether to ignore if a model is already in the
            process of being trained, default is False.
        :type force_retrain: bool
        """
        if not self._check_if_ml_model_is_already_training() or force_retrain:
            app.logger.info("{} | Training Bernoulli Naive Bayes "
                            "classifier...".format(self.project_name))

            self.ml_model = BernoulliNB()
            self.fetch_data()
            data, label_field = self.prepare_data(self.ml_data)

            if not data:
                app.logger.info(
                    "{} | No data found for training the ML algorithm"
                    "".format(self.project_name))
            else:
                model = self._save_ml_model(training=True)

                # Normalise the data and separate the target field
                data = pd.json_normalize(data)
                ml_data = data.drop(label_field, axis=1)
                label_values = data[label_field]

                app.logger.info("{} | Fitting model...".format(
                    self.project_name))
                self.ml_model.partial_fit(
                    ml_data, label_values, classes=list(self.labels.values()))

                app.logger.info("{} | Model fitted".format(self.project_name))
                self._save_ml_model(doc_id=model.id, ml_model=self.ml_model)
        else:
            app.logger.info(
                "{} | A Bernoulli Naive Bayes classifier is already in the "
                "process of being trained".format(self.project_name))

    def predict(self, data):
        """Returns the prediction of the Bernoulli Naive Bayes classifier from
        the passed in data.

        :param data: Data to use for the prediction.
        :type data: dict

        :return: Target field prediction.
        """
        self._check_for_new_ml_model()

        if not self.ml_model:
            app.logger.warning(
                'No machine learning models found for project: {}'.format(
                    self.project_name))
            return

        data, label_field = self.prepare_data(
            data, ignore_unclassified=False)

        if not data:
            app.logger.info("{} | No data valid data found to make a "
                            "prediction".format(self.project_name))

        # Normalise the data and separate the target field
        data = pd.json_normalize(data)
        ml_data = data.drop(label_field, axis=1)

        prediction = self.ml_model.predict(ml_data)

        # Retrieve the label from the numeric prediction value
        for label, numeric_label in self.labels.items():
            if numeric_label == prediction:
                return label
