from flask import current_app as app

from app.projects.urine_dipstick_analysis.urine_dipstick_model import UrineDipstickModel
from app import celery


class UrineDipstickAnalysis:
    """Urine dipstick diagnosis project for diagnosing urinary tract infection."""

    PROJECT_NAME = "UrineDipstickAnalysis"

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB."""

        app.logger.info("{} | Saving a new model with the data: {}".format(
            UrineDipstickAnalysis.PROJECT_NAME, data))

        model = UrineDipstickModel(user_id=current_user.id, **data)
        model.save()

        return model
