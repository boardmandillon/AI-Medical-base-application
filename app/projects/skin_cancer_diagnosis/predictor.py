from tensorflow import keras
import numpy as np

from keras_preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.models import load_model
from pathlib import Path

IMG_HEIGHT = 224
IMG_WIDTH = 224


def predict_image(image):
    """ Takes no arguments.
        Predicts the classification of the a image

        Takes the file as input and pre-processes the image
            - COLOUR_NORMALIZATION
            - IMG_HEIGHT = 224
            - IMG_WIDTH = 224

        The classification prediction output is formatted to a percentage and
        then returned.
    """
    model = load_model(Path("app/projects/skin_cancer_analysis/model.h5"))
    prediction = model.predict_generator(image)

    prediction = np.round(prediction, 2)
    prediction = str(prediction)[2:-2]
    readable_prediction = float(prediction) * 100
    prediction = str(readable_prediction)

    return prediction
