'''
Created on Jan 14, 2017

@author: safdar
'''
import numpy as np
import cv2

class ColorHistogram(object):
    def __init__(self, color_space='RGB', nbins=32, bins_range=(0, 256)):
        self.__color_space__ = color_space
        self.__nbins__ = nbins
        self.__bins_range__ = bins_range
        
    def extract(self, image):
        # apply color conversion if other than 'RGB'
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
        # Compute the histogram of the color channels separately
        channel1_hist = np.histogram(image[:,:,0], bins=self.__nbins__, range=self.__bins_range__)
        channel2_hist = np.histogram(image[:,:,1], bins=self.__nbins__, range=self.__bins_range__)
        channel3_hist = np.histogram(image[:,:,2], bins=self.__nbins__, range=self.__bins_range__)
        # Concatenate the histograms into a single feature vector
        hist_features = np.concatenate((channel1_hist[0], channel2_hist[0], channel3_hist[0]))
#         print ("\tColor histogram = {} slots".format(len(hist_features)))
        return hist_features
