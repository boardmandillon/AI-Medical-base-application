import numpy
import tensorflow
import numpy as np

from keras_preprocessing.image import ImageDataGenerator
from tensorflow_core.python.keras.models import load_model

IMG_HEIGHT = 224
IMG_WIDTH = 224
batch_size = 50
numpy.set_printoptions(threshold=2000)


def predictImage():
    imageDirectory = r'image'

    data_generator = ImageDataGenerator(preprocessing_function=
                                        tensorflow.keras.applications.mobilenet.preprocess_input)

    img = data_generator.flow_from_directory(directory=imageDirectory,
                                             shuffle=False,
                                             target_size=(IMG_HEIGHT, IMG_WIDTH),
                                             class_mode=None
                                             )

    model = load_model("model.h5")
    pred = model.predict_generator(img)
    # print(pred)
    pred = np.round(pred, 2)
    # print(pred)
    pred = str(pred)[2:-2]
    readablePred = float(pred) * 100
    # print("The Prediction of the input image: ", float(pred) * 100)
    return readablePred
