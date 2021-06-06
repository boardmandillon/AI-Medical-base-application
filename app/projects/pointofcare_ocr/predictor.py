import cv2
import imutils
import numpy as np
from app.projects.pointofcare_ocr.NumberROI import NumberROI
from tensorflow.keras.models import load_model
from app.projects.pointofcare_ocr.NumberRegion import NumberRegion

def predict(monitor_type, filename):
    preprocessed_digits = list ()
    number_list = list ()
    predict_numbers = list ()

    image = cv2.imread(filename)
    img_resize = imutils.resize(image, height=300)

    if monitor_type == "kinetik":
        img_resize = cv2.addWeighted(img_resize.copy(), 0.3, np.zeros(img_resize.shape, img_resize.dtype), 0,0)
        grey = cv2.cvtColor ( img_resize.copy() , cv2.COLOR_BGR2GRAY )
        blurred = cv2.GaussianBlur ( grey.copy () , (13 , 13) , 0 )
        thresh = cv2.threshold ( blurred.copy () , 0 , 255 , cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU )[1]
    else:
        grey = cv2.cvtColor (img_resize.copy () , cv2.COLOR_BGR2GRAY )
        blurred = cv2.GaussianBlur ( grey.copy () , (17 , 17) , 0 )
        thresh = cv2.adaptiveThreshold ( blurred.copy () , 255 , cv2.ADAPTIVE_THRESH_MEAN_C ,
                                     cv2.THRESH_BINARY_INV , 11 ,2 )

    contours = cv2.findContours ( thresh.copy () , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE )
    contours = imutils.grab_contours ( contours )
    sorted_cnts = sorted (contours , key=cv2.contourArea , reverse=True )
    digitsCnts = list ()

    for c in sorted_cnts:
        (x , y , w , h) = cv2.boundingRect ( c )
        if monitor_type == "omron_rs4":
            if (x < 166) :
                if (w >= 0 and w < 187) and (h >= 15 and h <= 110) :
                    number_tuple = (x , y , w , h)
                    digitsCnts.append ( number_tuple )
        elif monitor_type == "kinetik" :
            if x > 60 and h > 10 :
                number_tuple = (x , y , w , h)
                digitsCnts.append ( number_tuple )
        elif monitor_type == "a&d" :
            if (w >= 10 and w <= 50) and (h >= 40 and h <= 110) :
                number_tuple = (x , y , w , h)
                digitsCnts.append ( number_tuple )

    number_id = 1
    # digitsCnts.sort ( key=operator.itemgetter ( 0 ) , reverse=True )
    # digitsCnts.sort ( key=operator.itemgetter ( 1 ) )

    for d in digitsCnts :
        number_roi = NumberROI( number_id , d[0] , d[1] , d[2] , d[3] , 0 )
        number_list.append ( number_roi )
        number_id += 1

    # print(number_list)
    for elem in number_list:
        x = elem.x
        y = elem.y
        w = elem.w
        h = elem.h
        digit = thresh[y :y + h , x :x + w]
        resized_digit = cv2.resize ( digit , (20 , 20) )
        inverted_digit = cv2.bitwise_not ( resized_digit )
        preprocessed_digits.append ( inverted_digit )

    model = load_model("app/projects/pointofcare_ocr/model_1.h5")
    for i in range(len(preprocessed_digits)) :
        prediction = model.predict(preprocessed_digits[i].reshape( 1 , 20 , 20 , 1 ))
        predict_numbers.append ( np.argmax ( prediction ) )
        number_list[i].update_prediction ( np.argmax ( prediction ))

    outcome = list()
    if monitor_type == "omron_rs4":
        image = image[0 :300 , 0 :170]

    gray = cv2.cvtColor (image.copy () , cv2.COLOR_BGR2GRAY )

    # threshold the grayscale image
    thresh = cv2.threshold ( gray , 0 , 255 , cv2.THRESH_BINARY + cv2.THRESH_OTSU )[1]

    # use morphology erode to blur horizontally
    kernel = cv2.getStructuringElement ( cv2.MORPH_RECT , (10 , 3) )
    morph = cv2.morphologyEx ( thresh , cv2.MORPH_DILATE , kernel )

    # find contours
    cntrs = cv2.findContours ( morph , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE )
    cntrs = cntrs[0] if len ( cntrs ) == 2 else cntrs[1]

    number_regions = list ()
    i = 1
    for c in cntrs :
        (x , y , w , h) = cv2.boundingRect ( c )
        if monitor_type != "omron_rs4" :
            if x > 60 :
                number_region = NumberRegion ( i , x , y , w , h , list () )
                number_regions.append ( number_region )
                i += 1
        else :
            number_region = NumberRegion ( i , x , y , w , h , list () )
            number_regions.append ( number_region )
            i += 1

    for i in range ( len ( number_regions ) ) :
        region_x = number_regions[i].x
        region_y = number_regions[i].y
        region_w = number_regions[i].w
        region_h = number_regions[i].h
        for j in range (len(number_list)) :
            if (region_x <= number_list[j].x <= region_x + region_w) and \
                    (region_y <= number_list[j].y <= region_y + region_h) :
                number_regions[i].add_number ( number_list[j].unique_id )

    for i in range ( len ( number_regions ) ) :
        num_list = number_regions[i].number_list
        number_str = ""
        for elem in num_list :
            for j in range ( len ( number_list ) ) :
                if number_list[j].unique_id == elem :
                    number_str += str ( number_list[j].prediction )
        outcome.append ( number_str )
        print ( number_str )
    print(outcome)
    return outcome


