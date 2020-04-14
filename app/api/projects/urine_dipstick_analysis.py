from flask import request, g
from flask import jsonify

from app.api import bp
from app.api.auth import token_auth
from app.projects.urine_dipstick_analysis.urine_dipstick_model import \
    UrineDipstickModel
from app.api.errors import bad_request
from PIL import Image
import io
import base64
import binascii
import bson
import numpy as np
from cv2 import cv2 as cv
import imutils
import os


@bp.route('/urine_dipstick_analysis/', methods=['POST'])
@token_auth.login_required
def upload_urine_analysis_image():
    """Extracts urine dipstick image from JSON data in the request.

    Decodes a base64 encoded image into binary form before sending
    to the project model. Verification of binary image data is done by
    PIL library.
    """
    data = request.get_json() or {}

    if not data.get('photo_base64'):
        return bad_request('must include content type and photo data in request')
    photo_base64 = data.get('photo_base64')

    try:
        diagnosis_photo = base64.b64decode(photo_base64, validate=True)
    except binascii.Error:
        return bad_request('failed to decode base64 string')
    del data['photo_base64']

    try:
        image = Image.open(io.BytesIO(diagnosis_photo))
        image.verify()
        content_type = image.format
        image.close()
    except IOError:
        return bad_request('image file is not valid')

    diagnosis = UrineDipstickModel(user_id=g.current_user.id, content_type=content_type,
                                   **data, diagnosis_photo=diagnosis_photo)
    diagnosis.save()

    return diagnosis.to_json(), 201


@bp.route('/urine_dipstick_analysis/', methods=['GET'])
@token_auth.login_required
def get_urine_analysis():
    """Retrieves analysis image corresponding to a given document object ID
    passed as a URL parameter.

    For example <base URL>/urine_dipstick_analysis_images?id=<object ID here>
    """
    data = request.args.to_dict()

    if not data.get('id'):
        return bad_request('must include image file id')
    object_id = data.get('id')

    if not UrineDipstickModel.objects.get(
            user_id=g.current_user.id,
            diagnosis_photo=bson.objectid.ObjectId(object_id)):
        return bad_request('no file with the id: ' + data.get('id') + ' for this user')

    user_data = UrineDipstickModel.objects.get(
        user_id=g.current_user.id, diagnosis_photo=bson.objectid.ObjectId(object_id))
    diagnosis_photo = user_data.diagnosis_photo.read()
    content_type = user_data.content_type

    image_pre_processing(diagnosis_photo)

    data = {'message': 'image retrieved successfully'}
    return jsonify(data), 200


def image_pre_processing(diagnosis_photo):
    np_array = np.frombuffer(diagnosis_photo, dtype=np.uint8)
    image = cv.imdecode(np_array, flags=1)

    contours = get_image_contours(image)
    dipstick_contour = get_dipstick_contour(contours)
    dipstick = retrieve_dipstick_image(image, dipstick_contour)

    print("Shape: {}".format(dipstick.shape))

    out_filepath = '/Users/Miles/Desktop/'
    cv.imwrite(os.path.join(out_filepath, 'test.jpg'), dipstick)


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

    return dipstick_contour


def retrieve_dipstick_image(image, contour):
    """ Calculate the minimum area bounding the dipstick image, then apply a
    rotation matrix to straighten the rectangle. If the dipstick has been rotated
    into a vertical position it is rotated anticlockwise. The horizontal dipstick
    image is then resized for extracting squares on the dipstick.
    """
    rectangle = cv.minAreaRect(contour)
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
