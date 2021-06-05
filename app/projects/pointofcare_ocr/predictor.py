import operator
import cv2
import imutils
import numpy as np
from app.projects.pointofcare_ocr.NumberROI import NumberROI
from pathlib import Path
import keras
from tensorflow.keras.models import load_model

preprocessed_digits = list ()
number_list = list ()
predict_numbers = list ()

def predict(monitor_type, filename):
    image = cv2.imread(filename)
    image = imutils.resize(image, height=300)
    grey = cv2.cvtColor ( image.copy () , cv2.COLOR_BGR2GRAY )
    blurred = cv2.GaussianBlur ( grey.copy () , (17 , 17) , 0 )
    thresh = cv2.adaptiveThreshold ( blurred.copy () , 255 , cv2.ADAPTIVE_THRESH_MEAN_C ,
                                     cv2.THRESH_BINARY_INV , 11 ,2 )
    contours = cv2.findContours ( thresh.copy () , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE )
    contours = imutils.grab_contours ( contours )
    digitsCnts = list ()

    for c in contours :
        (x , y , w , h) = cv2.boundingRect ( c )
        if monitor_type == "omron_rs4" :
            if (x < 166) :
                if (w >= 0 and w < 187) and (h >= 15 and h <= 110) :
                    number_tuple = (x , y , w , h)
                    digitsCnts.append ( number_tuple )
        elif monitor_type == "kinetik" :
            number_tuple = (x , y , w , h)
            digitsCnts.append ( number_tuple )
        elif monitor_type == "a&d" :
            if (w >= 10 and w <= 50) and (h >= 40 and h <= 110) :
                number_tuple = (x , y , w , h)
                digitsCnts.append ( number_tuple )

    number_id = 1
    digitsCnts.sort ( key=operator.itemgetter ( 0 ) , reverse=True )
    digitsCnts.sort ( key=operator.itemgetter ( 1 ) )

    for d in digitsCnts :
        number_roi = NumberROI( number_id , d[0] , d[1] , d[2] , d[3] , 0 )
        number_list.append ( number_roi )
        number_id += 1

    for elem in number_list :
        x = elem.x
        y = elem.y
        w = elem.w
        h = elem.h
        digit = thresh[y :y + h , x :x + w]
        resized_digit = cv2.resize ( digit , (20 , 20) )
        inverted_digit = cv2.bitwise_not ( resized_digit )
        preprocessed_digits.append ( inverted_digit )

    detect_digits()
    return put_together()


def detect_digits() :
    model = load_model("app/projects/pointofcare_ocr/model_1.h5")
    for i in range ( len ( preprocessed_digits ) ) :
        prediction = model.predict(preprocessed_digits[i].reshape( 1 , 20 , 20 , 1 ))
        predict_numbers.append ( np.argmax ( prediction ) )
        number_list[i].update_prediction ( np.argmax ( prediction ))

def put_together():
    outcome = list ()
    taken = list ()
    for i in range ( len ( number_list ) ) :
        if number_list[i].unique_id in taken :
            continue
        else:
            taken.append ( number_list[i].unique_id )
            reading = ""
            reading += str ( number_list[i].predicted )
            if number_list[i].predicted > 1 :
                reading += str ( number_list[i + 1].predicted )
                taken.append ( number_list[i + 1].unique_id )
            else :
                reading += str ( number_list[i + 1].predicted ) + str ( number_list[i + 2].predicted )
                taken.append ( number_list[i + 1].unique_id )
                taken.append ( number_list[i + 2].unique_id )
        outcome.append ( reading[: :-1] )
    return outcome


