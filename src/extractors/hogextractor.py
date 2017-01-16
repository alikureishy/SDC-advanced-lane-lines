'''
Created on Jan 14, 2017

@author: safdar
'''
from skimage.feature._hog import hog
import cv2

class HogExtractor(object):
    def __init__(self, orientations=9, hog_channel=0, pixels_per_cell=8, cells_per_block=2):
        self.__orientations__ = orientations
        self.__pixels_per_cell__ = pixels_per_cell
        self.__cells_per_block__ = cells_per_block
        self.__hog_channel__ = hog_channel
        
    def extract(self, image):
        image = cv2.resize(image, (32, 32))
        features = hog(image[:,:,self.__hog_channel__],
                       orientations=self.__orientations__,
                       pixels_per_cell=(self.__pixels_per_cell__, self.__pixels_per_cell__),
                       cells_per_block=(self.__cells_per_block__, self.__cells_per_block__),
                       transform_sqrt=True,
                       visualise=False, feature_vector=True)
#         print ("\tHOG Features = {} slots".format(len(features)))
        return features
