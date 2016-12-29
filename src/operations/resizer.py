'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import cv2

class Resizer(Operation):
    TargetShape = 'TargetShape'

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__targetshape__ = self.getparam(self.TargetShape)
        assert len(self.__targetshape__) == 2, "Shape was supposed to be [x, y] but was {}".format(self.__targetshape__)

    def __processupstream__(self, original, latest, data, frame):
        latest = cv2.resize(latest, (self.__targetshape__[1], self.__targetshape__[0]), interpolation = cv2.INTER_AREA)
        title = "Resized to {}".format(self.__targetshape__)
        stats = None
        self.__plot__(frame, latest, None, title, stats)
        return latest
        