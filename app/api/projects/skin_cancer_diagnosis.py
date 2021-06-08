from PIL import Image
from flask import request, jsonify
from flask_jwt_extended import (jwt_required)

from app.api import bp
from app.projects.skin_cancer_diagnosis import predictor


@bp.route('/skin-cancer-diagnosis', methods=['POST'])
@jwt_required()
def diagnose_skin_lesion():
    """
    Extracts lesion image from JSON data in the request.
    Verification of image data is done by PIL library.
    """
    if not request.files:
        return jsonify(), 400

    file = request.files['image']
    image = Image.open(file)

    prediction = predictor.predict_image(image)
    return jsonify(prediction), 201
