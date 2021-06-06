"""Object represent a number found in the image
"""
class NumberROI:
    def __init__(self, unique_id, x, y, w, h, prediction):
        self.unique_id = unique_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.prediction = prediction

    def __iter__(self):
        return self

    def update_prediction(self, new_prediction):
        self.prediction = new_prediction
