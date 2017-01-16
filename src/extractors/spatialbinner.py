'''
Created on Jan 14, 2017

@author: safdar
'''
import cv2
import numpy as np

class SpatialBinner(object):
    def __init__(self, color_space='RGB', size=(32, 32)):
        self.__color_space__ = color_space
        self.__size__ = size
    
    def extract(self, image):
        if self.__color_space__ == 'RGB':
            image = np.copy(image)
        if self.__color_space__ == 'BGR':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif self.__color_space__ == 'HSV':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif self.__color_space__ == 'HLS':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        elif self.__color_space__ == 'YUV':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        image = cv2.resize(image, tuple(self.__size__))
        features = image.ravel()
#         print ("\tSpatial bins = {} slots".format(len(features)))
        return features
        