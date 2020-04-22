import numpy as np
from cv2 import cv2 as cv
from sklearn.cluster import KMeans
from collections import Counter
from skimage.color import rgb2lab
import colour
from pathlib import Path
import os


def squares_colour_detection(dipstick_squares):

    for index, square in enumerate(dipstick_squares):
        out_filepath = '/Users/Miles/Desktop/Squares/'
        cv.imwrite(os.path.join(out_filepath, 'square' + str(index) + '.jpg'), square)

    dipstick_squares_colours = get_dominant_colour(dipstick_squares)
    training_images = load_training_images()
    test_group_colours = []
    for test_category in training_images:
        training_images_colours = get_dominant_colour(test_category)
        test_group_colours.append(training_images_colours)

    minimum_indices = match_image_by_colour(dipstick_squares_colours, test_group_colours)
    print(minimum_indices)


def get_dominant_colour(images):
    """ Extracts the most dominant RGB colour from each square image using the KMeans
    algorithm. The image is first converted from BGR to RGB and resized to two dimensions
    as this is how KMeans expects the input. Clusters are formed based on the colours in
    each image, which are ordered and the most dominant colour is added to the returned list.
    """
    number_of_colours = 1
    dominant_colours = []
    for square in images:
        square = cv.cvtColor(square, cv.COLOR_BGR2RGB)
        modified_square = square.reshape(square.shape[0] * square.shape[1], 3)
        clusters = KMeans(n_clusters=number_of_colours)
        labels = clusters.fit_predict(modified_square)

        counts = Counter(labels)
        cluster_colours = clusters.cluster_centers_

        ordered_colors = [cluster_colours[index] for index in counts.keys()]
        rgb_colors = [ordered_colors[index] for index in counts.keys()]

        dominant_colours.append(rgb_colors)

    return dominant_colours


def load_training_images():
    """ Loads in the training images for each of the test groups from a directory.
    Returns a nested list, the outer list refers to the test groups and the inner
    sub-lists contain images for all possible outcomes for a particular test.
    """
    training_images = []
    cwd = Path(__file__).parent.absolute()
    image_directory = str(cwd) + '/training_images/'

    for directory in sorted(os.listdir(image_directory)):
        if not directory.startswith('.'):
            test_category = []
            for file in sorted(os.listdir(image_directory + directory)):
                if not file.startswith('.'):
                    image_path = image_directory + directory + '/' + file
                    image = cv.imread(image_path)
                    test_category.append(image)
            training_images.append(test_category)

    return training_images


def match_image_by_colour(images, training_images):
    """ Loops through each test category comparing each square extracted from
    the dipstick with all possible test outcomes, in order to find the two closest
    matching colours for each test. To make the colour comparison RGB colours are
    converted to LAB colours and the LAB DELTA E 2000 formula is computed. A list
    is returned containing the indices corresponding to which colours for each test
    had the closet match.
    """
    minimum_indices = []
    minimum = 0
    for index, test_category in enumerate(training_images):
        minimum_delta_e = 101
        for minimum_index, test in enumerate(test_category):
            square_colour = rgb2lab(np.uint8([[images[index]]]))
            test_colour = rgb2lab(np.uint8([[test]]))

            delta_e = colour.delta_E(square_colour, test_colour)
            if delta_e < minimum_delta_e:
                minimum_delta_e = delta_e
                minimum = minimum_index

        minimum_indices.append(minimum)

    return minimum_indices
