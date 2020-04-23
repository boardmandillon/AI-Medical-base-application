from flask import current_app as app

from app.projects.skin_cancer_analysis.skin_cancer_model import skinCancerModel
from app import celery


class SkinCancerAnalysis:
    """Skin Cancer diagnosis project for diagnosing urinary tract infection."""

    PROJECT_NAME = "SkinCancerAnalysis"

    @staticmethod
    def _save_data(data, current_user):
        """Save the passed in data to MongoDB."""

        app.logger.info("{} | Saving a new model with the data: {}".format(
            SkinCancerAnalysis.PROJECT_NAME, data))

        model = skinCancerModel(user_id=current_user.id, **data)
        model.save()

        return model
