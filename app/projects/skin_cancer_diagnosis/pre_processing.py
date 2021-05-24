
# color_constancy function is adapted from isic2018-skin-lesion-classifier-tensorflow
## Author: Abhishek Rana
## Date: 22/04/2021
## Name: utils_image.py
## Type: source code
## Web address: https://github.com/abhishekrana/isic2018-skin-lesion-classifier-tensorflow/blob/master/utils/utils_image.py

import os

import cv2
import numpy as np
from PIL import Image

IMG_PATH = os.path.join(os.getcwd(), 'image.png')


def color_constancy(image, power=6):
    image = image.astype('float32')
    image_power = np.power(image, power)

    rgb_vec = np.power(np.mean(image_power, (0, 1)), 1 / power)
    rgb_norm = np.sqrt(np.sum(np.power(rgb_vec, 2.0)))
    rgb_vec = rgb_vec / rgb_norm
    rgb_vec = 1 / (rgb_vec * np.sqrt(3))

    image = np.multiply(image, rgb_vec)
    image = np.clip(image, a_min=0, a_max=255)

    return image.astype(image.dtype)


def pre_process_image(image):
    # convert to cv2 image
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # apply pre-processing and save (saving due to problems with BGR conversion)
    pre_processed_image = color_constancy(image)
    cv2.imwrite(IMG_PATH, pre_processed_image)

    # open image and then delete
    pre_processed_image = Image.open(IMG_PATH)
    os.remove(IMG_PATH)

    return pre_processed_image
