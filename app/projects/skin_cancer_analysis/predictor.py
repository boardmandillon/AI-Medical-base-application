from tensorflow import keras
import numpy as np

from keras_preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.models import load_model

IMG_HEIGHT = 224
IMG_WIDTH = 224


def predictImage():
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
