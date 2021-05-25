"""Object represent a number found in the image
"""
class NumberROI:
    def __init__(self, unique_id, x, y, w, h, predicted):
        self.unique_id = unique_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.predicted = predicted

    def __iter__(self):
        return self

    def update_prediction(self, new_prediction):
        self.predicted = new_prediction
