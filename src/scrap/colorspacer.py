'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import cv2

class ColorSpacer(Operation):
    Original = 'Original'
    Target = 'Target'
    Transforms = {
        "RGB2BGR" : cv2.COLOR_RGB2BGR,
        "RGB2HLS" : cv2.COLOR_RGB2HLS,
        "RGB2HSV" : cv2.COLOR_RGB2HSV,
        "RGB2YUV" : cv2.COLOR_RGB2YUV,
        "BGR2RGB" : cv2.COLOR_BGR2RGB,
        "BGR2HLS" : cv2.COLOR_BGR2HLS,
        "BGR2HSV" : cv2.COLOR_BGR2HSV,
        "BGR2YUV" : cv2.COLOR_BGR2YUV,
        "HLS2BGR" : cv2.COLOR_HLS2BGR,
        "HLS2RGB" : cv2.COLOR_HLS2RGB,
        "HSV2BGR" : cv2.COLOR_HSV2BGR,
        "HSV2RGB" : cv2.COLOR_HSV2RGB,
        "YUV2BGR" : cv2.COLOR_YUV2BGR,
        "YUV2RGB" : cv2.COLOR_YUV2RGB
    }

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__original__ = self.getparam(self.Original)
        self.__target__ = self.getparam(self.Target)
        forward = "{}2{}".format(self.__original__, self.__target__)
        if not forward in self.Transforms:
            raise "Forward transformation {} -> {} is not supported. Please try another.".format(self.__original__,self.__target__)
        self.__forward__ = self.Transforms[forward]
        backward = forward[::-1]
        if not backward in self.Transforms:
            raise "Reverse transformation {} -> {} is not supported. Please try another.".format(self.__target__, self.__original__)
        self.__backward__ = self.Transforms[backward]

    def __processupstream__(self, original, latest, data, frame):
        latest = cv2.cvtColor(latest, self.__forward__)
        title = "ColorSpace {}->{}".format(self.__original__,self.__target__)
        stats = None
        self.__plot__(frame, latest, None, title, stats)
        return latest

    def __processdownstream__(self, original, latest, data, frame):
        latest = cv2.cvtColor(latest, self.__backward__)
        title = "ColorSpace {}->{}".format(self.__target__, self.__original__)
        stats = None
        self.__plot__(frame, latest, None, title, stats)
        return latest
        