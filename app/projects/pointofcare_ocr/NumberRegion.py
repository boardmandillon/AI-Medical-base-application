"""Object represent a block of numbers
"""
class NumberRegion:
    def __init__(self, unique_id, x, y, w, h, number_list):
        self.unique_id = unique_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.number_list = number_list

    def __iter__(self):
        return self

    def add_number(self, number_id):
        self.number_list.append(number_id)