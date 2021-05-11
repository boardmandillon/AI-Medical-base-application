from flask import current_app as app

import json
from app.projects.pointofcare_ocr.pointofcare_model import POC_OCR_Model
from app.projects.example_project.example_model import ExampleModel
from app.machine_learning.decision_tree import DecisionTree
from app import celery


class PointOfCareOCR:
    """Point of care OCR project class for uploading results from PoC device to electronic record """

    PROJECT_NAME = "PointOfCareOCR"

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB."""

        app.logger.info(
            "{} | Saving a new model with the data: {}".format(
                PointOfCareOCR.PROJECT_NAME, data))

        model = POC_OCR_Model(user_id=current_user['id'], **data)
        model.save()

        return model

    # insert algorithm here
    @staticmethod
    def read_picture(self, data, current_user ):
        pass
