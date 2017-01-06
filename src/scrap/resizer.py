'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import cv2

class Resizer(Operation):
    TargetShapeRatio = 'TargetShapeRatio'

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__targetshaperatio__ = self.getparam(self.TargetShapeRatio)
        self.__targetshape__ = None
        self.__originalshape__ = None
        assert len(self.__targetshaperatio__) == 2, "Shape was supposed to be [x, y] but was {}".format(self.__targetshaperatio__)

    def __processupstream__(self, original, latest, data, frame):
        if self.__targetshape__ is None:
            self.__targetshape__ = (int(self.__targetshaperatio__[1] * latest.shape[1]), int(self.__targetshaperatio__[0] * latest.shape[0])) 
            self.__originalshape__ = latest.shape
        latest = cv2.resize(latest, self.__targetshape__, interpolation = cv2.INTER_AREA)
        title = "Resized to {}".format(self.__targetshape__)
        stats = None
        self.__plot__(frame, latest, None, title, stats)
        return latest

    def __processdownstream__(self, original, latest, data, frame):
        latest = cv2.resize(latest, self.__originalshape__, interpolation = cv2.INTER_AREA)
        title = "Resized to {}".format(self.__originalshape__)
        stats = None
        self.__plot__(frame, latest, None, title, stats)
        return latest
        
        