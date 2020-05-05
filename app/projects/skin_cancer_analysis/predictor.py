from tensorflow import keras
import numpy as np

from keras_preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.models import load_model

IMG_HEIGHT = 224
IMG_WIDTH = 224


def predictImage():
    """ Takes no arguments.
        Predicts the classification of the image in the directory:

        'app\projects\skin_cancer_analysis\image'

        Note: The filepath above is used for windows.
        If the directory is not found, reverse the '\'
        e.g.

        'app/projects/skin_cancer_analysis/image'

        Takes the file as input and pre-processes the image through the
        ImageDataGenerator.

        IMG_HEIGHT = 224
        IMG_WIDTH = 224

        The target size of the image flowing from the directory above.

        The classification prediction output is rounded to 2 decimal places,
        stripped of the 2 characters either side of the value and multiplied
        by 100 to a percentage.

        The prediction is then returned.
    """
    imageDirectory = r'app\projects\skin_cancer_analysis\image'

    data_generator = ImageDataGenerator(preprocessing_function=keras.applications.mobilenet.preprocess_input)

    img = data_generator.flow_from_directory(directory=imageDirectory,
                                             shuffle=False,
                                             target_size=(IMG_HEIGHT, IMG_WIDTH),
                                             class_mode=None
                                             )

    model = load_model(r"app\projects\skin_cancer_analysis\model.h5")
    pred = model.predict_generator(img)

    pred = np.round(pred, 2)
    pred = str(pred)[2:-2]
    readablePred = float(pred) * 100
    prediction = str(readablePred)

    return prediction
