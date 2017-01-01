'''
Created on Dec 23, 2016

@author: safdar
'''
import numpy as np
from operations.baseoperation import Operation
import cv2
from operations.colorspacer import ColorSpacer
from utils.utilities import plotboundary

class RegionMasker(Operation):
    RelativePoints = 'RelativePoints'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__relativepoints__ = []
        for tup in params[self.RelativePoints]:
            if not len(tup)==2:
                raise "Invalid # of dimensions: {}".format(tup)
            [xratio, yratio] = tup
            self.__relativepoints__.append((xratio, yratio))

    def __processupstream__(self, original, latest, data, frame):
        mask = np.zeros_like(latest, dtype=np.int32)   # blank mask
        
        cmap = None
        if len(latest.shape) > 2: # if image is color (3 channels) create a color mask
            channel_count = latest.shape[2]  # i.e. 3 or 4 depending on your image
            ignore_mask_color = (255,) * channel_count
        else:   # if image is not color, create a grayscale mask
            ignore_mask_color = 255
            cmap = 'gray'

        x_dim = latest.shape[1]
        y_dim = latest.shape[0]
        vertices = np.array([[ (xr*x_dim, yr*y_dim) for [xr,yr] in self.__relativepoints__]],dtype=np.int32)

        if self.isplotting():
            orig = np.copy(self.getdata(data, self.Upstream, ColorSpacer))
            plotboundary(orig, vertices[0], (127, 255, 212))
            self.__plot__(frame, orig, None, "Region Mask (Color)", None)

        # Fix ordering for the fillpoly method:
        tmp = vertices[0][0]
        vertices[0][0] = vertices[0][1]
        vertices[0][1] = tmp
        mask = cv2.fillPoly(mask, vertices, ignore_mask_color) #filling pixels inside the polygon defined by "vertices" with the fill color

        #returning the image only where mask pixels are nonzero
        masked_image = np.float32(latest*mask)
        
        title = "RegionMasker {}".format(self.__relativepoints__)
        stats = None
        self.__plot__(frame, masked_image, cmap, title, stats)
        
        return masked_image
