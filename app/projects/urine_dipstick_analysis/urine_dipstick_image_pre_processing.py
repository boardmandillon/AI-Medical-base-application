import numpy as np
from cv2 import cv2 as cv
import imutils


def image_pre_processing(diagnosis_photo):
    """ Extracts the urine dipstick in the uploaded image, if successful returns
    the ten squares found on the dipstick. Verification is done on the dipstick
    making sure it is both horizontal and in reasonable lighting.
    """
    np_array = np.frombuffer(diagnosis_photo, dtype=np.uint8)
    image = cv.imdecode(np_array, flags=1)

    contours = get_image_contours(image)
    dipstick_contour, message = get_dipstick_contour(contours)

    if dipstick_contour is None and message == 'vertical':
        return False, 'dipstick should be horizontal not vertical'
    elif dipstick_contour is None:
        return False, 'failed to detect urine dipstick in uploaded image'

    dipstick = retrieve_dipstick_image(image, dipstick_contour)
    if dipstick is None:
        return False, 'failed to detect urine dipstick in uploaded image'

    verified, message = verify_dipstick(dipstick)
    if not verified and message == 'rectangle size':
        return False, 'failed to detect urine dipstick in uploaded image'
    elif not verified and message == 'lighting':
        return False, 'urine dipstick is in bad lighting or there is a shadow ' \
                      'in the uploaded image'

    dipstick_squares = get_dipstick_squares(dipstick)

    return True, dipstick_squares


def get_image_contours(image):
    """ Extracts contours from the image.

    Image is converted to a grayscale and a bilateral filter is applied to reduce noise
    and preserve edges. Then a canny filter is used to catch strong edges, contours are
    grabbed and the ten largest contours are retrieved based on area.
    """
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image_filtered = cv.bilateralFilter(image_gray, 15, 75, 75)
    image_edges = cv.Canny(image_filtered, 30, 200)

    contours = cv.findContours(image_edges.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv.contourArea, reverse=True)[:10]
    return contours


def get_dipstick_contour(contours):
    """ Searches contours for contour with four vertex points, rectangle/square shape.
    When a rectangle/square is detected compute the bounding box and aspect ratio to
    confirm its the rectangle dipstick.
    """
    dipstick_contour = None
    for contour in contours:
        perimeter = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.015 * perimeter, True)

        if len(approx) == 4:
            (x, y, width, height) = cv.boundingRect(approx)
            aspect_ratio = float(width) / height

            if aspect_ratio > 1.05:
                dipstick_contour = contour
                break
            elif aspect_ratio < 0.95:
                return None, 'vertical'

    return dipstick_contour, 'complete'


def retrieve_dipstick_image(image, contour):
    """ Calculate the minimum area bounding the dipstick image, then apply a
    rotation matrix to straighten the rectangle. If the dipstick has been rotated
    into a vertical position it is rotated anticlockwise. The horizontal dipstick
    image is then resized for extracting squares on the dipstick.
    """
    try:
        rectangle = cv.minAreaRect(contour)
    except cv.error:
        return None

    center, size, theta = rectangle
    height, width = image.shape[:2]

    center, size = tuple(map(int, center)), tuple(map(int, size))
    matrix = cv.getRotationMatrix2D(center, theta, 1)
    dst = cv.warpAffine(image, matrix, (width, height))
    dipstick = cv.getRectSubPix(dst, size, center)

    if dipstick.shape[0] > dipstick.shape[1]:
        dipstick = cv.rotate(dipstick, cv.ROTATE_90_COUNTERCLOCKWISE)

    dipstick = imutils.resize(dipstick, width=800)
    return dipstick


def verify_dipstick(dipstick):
    """ Verify that the dipstick doesn't exceed a height threshold and isn't a larger
    rectangle being detected. Extract a small section from the front and end of the
    dipstick to check the colour, in order to distinguish dipstick rectangle and check
    lighting conditions of image.
    """
    if dipstick.shape[0] > 60:
        return False, 'rectangle size'

    dipstick_start = dipstick[0:dipstick.shape[0], 0:15]
    dipstick_end = dipstick[0:dipstick.shape[0], 785:dipstick.shape[1]]

    start_rgb = rgb_values(dipstick_start)
    end_rgb = rgb_values(dipstick_end)
    lower_white = 192
    upper_white = 255
    for index in range(3):
        if not lower_white <= start_rgb[index] <= upper_white:
            return False, 'lighting'
        elif not lower_white <= end_rgb[index] <= upper_white:
            return False, 'lighting'

    return True, 'verification complete'


def rgb_values(image):
    """ Extracts the mean red, green and blue values from an image.
    """
    rgb = [np.mean(image[:, :, 2]), np.mean(image[:, :, 1]), np.mean(image[:, :, 0])]
    return rgb


def get_dipstick_squares(dipstick):
    """ Slices the dipstick image cropping out the ten squares on the dipstick
    based on their position and saving them to a list.
    """
    dipstick_squares = []

    square_start = 15
    square_end = 50
    square_size = 35
    distance_between_squares = 20
    next_square = (square_size + distance_between_squares)
    for index in range(10):
        square = dipstick[0:dipstick.shape[0], square_start:square_end]
        dipstick_squares.append(square)

        square_start += next_square
        square_end += next_square

    return dipstick_squares
