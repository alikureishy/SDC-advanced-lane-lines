'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation

class ShowOriginal(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        self.__plot__(frame, original, None, "Original: {}".format(original.shape), None)
        return latest
