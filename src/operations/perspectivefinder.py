'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import cv2
import numpy as np
from utils.utilities import extractlanes, drawlines
from utils.plotter import Image
from utils.plotter import Graph

class PerspectiveFinder(Operation):
    # Outputs
    class Outputs(object):
        LeftMarker = 'LeftMarker'
        RightMarker = 'RightMarker'
        PerspectivePoints = 'PerspectivePoints'
        TransformPoints = 'TransformPoints'
    
    # Config params
    HoughFilter = 'HoughFilter'
    DefaultPerspectiveRatios = 'DefaultPerspectiveRatios'
    TransformRatios = 'TransformRatios'

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__hough_filter_params__ = params[self.HoughFilter]
        self.__default_pers_ratios__ = params[self.DefaultPerspectiveRatios]
        self.__transform_ratios__ = params[self.TransformRatios]
        self.__perspective_defaults__ = None
        self.__perspective_points__ = None
        self.__transform_points__ = None

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim = latest.shape[1], latest.shape[0]
        lines, left, right = extractlanes(latest, self.__hough_filter_params__)

        # Calculate and cache the transform points:
        if self.__transform_points__ is None:
            self.__transform_points__ = [[x_ratio*x_dim, y_ratio*y_dim] for [x_ratio,y_ratio] in self.__transform_ratios__]
            self.__perspective_defaults__ = [[int(x_ratio*x_dim), int(y_ratio*y_dim)] for [x_ratio,y_ratio] in self.__default_pers_ratios__]

        # Determine perspective points:
        op = None
        perspective_points = None
        if not left is None and not right is None:
            self.__perspective_points__ = [[left[0][2], left[0][3]], \
                                          [right[0][2], right[0][3]], \
                                          [left[0][0], left[0][1]], \
                                          [right[0][0], right[0][1]]]
            op = '***'
            perspective_points = self.__perspective_points__
        elif not self.__perspective_points__ is None:
            # Use existing
            op = '<<<'
            perspective_points = self.__perspective_points__
        else:
            # Use default ratios:
            op = '~~~'
            perspective_points = self.__perspective_defaults__
            
        # Set the data for use down the pipeline        
        self.setdata(data, self.Outputs.LeftMarker, left)
        self.setdata(data, self.Outputs.RightMarker, right)
        self.setdata(data, self.Outputs.PerspectivePoints, perspective_points)
        self.setdata(data, self.Outputs.TransformPoints, self.__transform_points__)

        # Illustration:
        if self.isplotting():
#             empty = np.zeros((*latest.shape, 3), dtype=np.uint8)
            hough = drawlines (np.zeros_like(latest), lines, 255, 15)
            self.__plot__(frame, Image("Temp Hough", hough, 'gray'))

            perspective = drawlines (np.zeros_like(latest), [left, right], 255, 15)
            for i in range(len(perspective_points)):
                perspective = cv2.circle(perspective, tuple(perspective_points[i]), 10, (255,0,0), -1)
            title = "Perspective Points ({})".format(op)
            self.__plot__(frame, Image(title, perspective, 'gray'))
        
        return latest
        