'''
Created on Dec 23, 2016

@author: safdar
'''
import numpy as np
from operations.baseoperation import Operation
import cv2

class RegionMasker(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__ratios__ = []
        for rhs in params:
            (xratio, yratio) = self.getfloattuple(rhs)
            self.__relativepoints__.append((xratio, yratio))

    def __processinternal__(self, original, latest, data, frame):
        mask = np.zeros_like(latest)   # blank mask
        
        cmap = None
        if len(latest.shape) > 2: # if image is color (3 channels) create a color mask
            channel_count = latest.shape[2]  # i.e. 3 or 4 depending on your image
            ignore_mask_color = (255,) * channel_count
        else:   # if image is not color, create a grayscale mask
            ignore_mask_color = 255
            cmap = 'gray'

        x_dim = latest.shape[0]
        y_dim = latest.shape[1]
        vertices = [ (xr*x_dim, yr*y_dim) for [xr,yr] in self.__relavivepoints__]

        cv2.fillPoly(mask, vertices, ignore_mask_color) #filling pixels inside the polygon defined by "vertices" with the fill color

        #returning the image only where mask pixels are nonzero
        masked_image = cv2.bitwise_and(latest, mask)
        
        title = "RegionMasker {}".format(self.__relativepoints__)
        stats = None
        frame.add(masked_image, cmap, title, stats)
        
        return masked_image
