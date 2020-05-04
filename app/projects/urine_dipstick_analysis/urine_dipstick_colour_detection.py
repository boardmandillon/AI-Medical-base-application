import numpy as np
from cv2 import cv2 as cv
from sklearn.cluster import KMeans
from collections import Counter
from skimage.color import rgb2lab
import colour
from pathlib import Path
import os


def squares_colour_detection(dipstick_squares):
    """ Obtains the diagnosis results from the squares extracted from the uploaded image.
    Returns a dictionary containing ten results for each of the different test groups on
    the urine dipstick.
    """
    dipstick_squares_colours = get_dominant_colour(dipstick_squares)
    training_images = load_training_images()
    test_group_colours = []
    for test_category in training_images:
        training_images_colours = get_dominant_colour(test_category)
        test_group_colours.append(training_images_colours)

    minimum_indices = match_image_by_colour(dipstick_squares_colours, test_group_colours)
    diagnosis_results = convert_diagnosis_results(minimum_indices)

    return diagnosis_results


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


def convert_diagnosis_results(diagnosis_data):
    """ Translates the list of indices into human readable diagnosis results
    """
    leukocyctes_results = ['negative', 'trace', '+70 WBC μL', '++125 WBC μL',
                           '+++500 WBC μL']
    nitrate_results = ['negative', 'trace', 'positive']
    urobilinogen_results = ['0.1 mg/dL normal', '1 (16) mg/dL (μmol/L) normal',
                            '2 (33) mg/dL (μmol/L)', '4 (66) mg/dL (μmol/L)',
                            '8 (131) mg/dL (μmol/L)']
    protein_results = ['negative', 'trace', '+30 (0.3) mg/dL (g/L)',
                       '++100 (1,0) mg/dL (g/L)', '+++300 (3.0) mg/dL (g/L)',
                       '++++1000 (10) mg/dL (g/L)']
    ph_results = ['5', '6', '6.5', '7', '7.5', '8', '8.5']
    blood_results = ['negative', 'trace hemolysis', '+25 RBC/μL hemolysis',
                     '++80 RBC/μL hemolysis', '+++200 RBC/μL hemolysis',
                     '+10 RBC/μL non hemolysis', '++80 RBC/μL non hemolysis']
    specific_gravity_results = ['1.000', '1.005', '1.010', '1.015', '1.020',
                                '1.025', '1.030']
    ketones_results = ['negative', '+/-5 (0.5) mg/dL (mmol/L)',
                       '+15 (1.5) mg/dL (mmol/L)', '++40 (3.9) mg/dL (mmol/L)',
                       '+++80 (8) mg/dL (mmol/L)', '++++160 (16) mg/dL (mmol/L)']
    bilirubin_results = ['negative', '+', '++', '+++']
    glucose_results = ['negative', '+/-100 (5.5) mg/dL (mmol/L)',
                       '+250 (14) mg/dL (mmol/L)', '++500 (28) mg/dL (mmol/L)',
                       '+++1000 (55) mg/dL (mmol/L)', '++++2000 (111) mg/dL (mmol/L)']

    diagnosis_results = {'leukocyctes': leukocyctes_results[diagnosis_data[0]],
                         'nitrate': nitrate_results[diagnosis_data[1]],
                         'urobilinogen': urobilinogen_results[diagnosis_data[2]],
                         'protein': protein_results[diagnosis_data[3]],
                         'pH': ph_results[diagnosis_data[4]],
                         'blood': blood_results[diagnosis_data[5]],
                         'specific gravity':
                         specific_gravity_results[diagnosis_data[6]],
                         'ketones': ketones_results[diagnosis_data[7]],
                         'bilirubin': bilirubin_results[diagnosis_data[8]],
                         'glucose': glucose_results[diagnosis_data[9]]}

    return diagnosis_results
