'''
Created on Jan 14, 2017

@author: safdar
'''
from skimage.feature._hog import hog
import cv2
import numpy as np

class HogExtractor(object):
    def __init__(self, orientations=9, space='GRAY', channel=0, size=(64,64), pixels_per_cell=8, cells_per_block=2):
        self.__orientations__ = orientations
        self.__pixels_per_cell__ = pixels_per_cell
        self.__cells_per_block__ = cells_per_block
        self.__channel__ = channel
        self.__size__ = size
        self.__color_space__ = space
        
    def extract(self, image):
        image = cv2.resize(image, tuple(self.__size__))
        cspace = self.__color_space__
        if cspace == 'RGB':
            image = np.copy(image)
        elif cspace == 'BGR':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif cspace == 'HSV':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif cspace == 'HLS':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        elif cspace == 'YUV':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        elif cspace == 'GRAY':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
        if cspace == 'GRAY':
            features = hog(image,
                           orientations=self.__orientations__,
                           pixels_per_cell=(self.__pixels_per_cell__, self.__pixels_per_cell__),
                           cells_per_block=(self.__cells_per_block__, self.__cells_per_block__),
                           visualise=False, feature_vector=True)
        else:
            features = hog(image[:,:,self.__hog_channel__],
                           orientations=self.__orientations__,
                           pixels_per_cell=(self.__pixels_per_cell__, self.__pixels_per_cell__),
                           cells_per_block=(self.__cells_per_block__, self.__cells_per_block__),
                           visualise=False, feature_vector=True)
#         print ("\tHOG Features = {} slots".format(len(features)))
        return features
