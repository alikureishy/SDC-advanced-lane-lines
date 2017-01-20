'''
Created on Dec 21, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
import cv2
from utils.utilities import plotboundary
from utils.plotter import Image
from utils.plotter import Graph

# Default:
#  Left ds = (.26*x, -.33*y) = (332, -237)
#  Right ds = (-.32*x, -.33*y) = (x_dim-409, -237)

class PerspectiveTransformer(Operation):
    # Config
    DefaultHeadingRatios = 'DefaultHeadingRatios'
    DepthRangeRatio = 'DepthRangeRatio'
    TransformRatios = 'TransformRatios'
    
    # Outputs:
    WarpedColor = "WarpedColor"

    def __init__(self, params):
        Operation.__init__(self, params)
        
        self.__M__ = None
        self.__Minv__ = None
        self.__default_heading__ = params[self.DefaultHeadingRatios]
        self.__depth_range_ratios__ = params[self.DepthRangeRatio]
#         self.__default_pers_ratios__ = params[self.DefaultPerspectiveRatios]
        self.__transform_ratios__ = params[self.TransformRatios]
        self.__perspective_points__ = None
        self.__transform_points__ = None
        
    def __processupstream__(self, original, latest, data, frame):
        x_dim = latest.shape[1]
        y_dim = latest.shape[0]

        # Calculate and cache the transform and perspective points since these will never change:
        if self.__transform_points__ is None:
            y_1 = int(y_dim * self.__depth_range_ratios__[0])
            y_2 = int(y_dim * self.__depth_range_ratios__[1])
            
            left_x = int(x_dim * self.__default_heading__[0][0])
            left_slope = self.__default_heading__[0][1]

            right_x = int(x_dim * self.__default_heading__[1][0])
            right_slope = self.__default_heading__[1][1]

            # Formula is: x = my + b     [where m = dx/dy]
            left_x_1 = int(left_x - ((y_dim-y_1) * left_slope))
            left_x_2 = int(left_x - ((y_dim-y_2) * left_slope))
            right_x_1 = int(right_x - ((y_dim-y_1) * right_slope))
            right_x_2 = int(right_x - ((y_dim-y_2) * right_slope))

#             self.__perspective_points__ = [[int(x_ratio*x_dim), int(y_ratio*y_dim)] for [x_ratio,y_ratio] in self.__default_pers_ratios__]
            self.__perspective_points__ = [(left_x_2, y_2), (right_x_2, y_2), (left_x_1, y_1), (right_x_1, y_1)]
            self.__transform_points__ = [[int(x_ratio*x_dim), int(y_ratio*y_dim)] for [x_ratio,y_ratio] in self.__transform_ratios__]
            self.__M__, self.__Minv__ = self.gettransformations(self.__perspective_points__, self.__transform_points__)

        # Plot the source points, for the benefit of the viewer
        orig = np.copy(original)
        
        if self.isplotting():
            # Show perspective regions:
            orig_temp = np.copy(orig)
            plotboundary(orig_temp, self.__perspective_points__, (127, 255, 212))
            self.__plot__(frame, Image("Warp Region (Source)", orig_temp, None))

        # Warp the image:
        warped_orig = cv2.warpPerspective(orig, self.__M__, (x_dim, y_dim), flags=cv2.INTER_LINEAR)
        self.setdata(data, self.WarpedColor, warped_orig)
        
        if self.isplotting():
            # Show warped original:
            orig_temp = np.copy(warped_orig)
            plotboundary(orig_temp, self.__transform_points__, (255, 192, 203))
            self.__plot__(frame, Image("Warped (Original)", orig_temp, None))
            
        # Perform perspective transform:
        bw_warped = cv2.warpPerspective(np.float32(latest), self.__M__, (x_dim, y_dim), flags=cv2.INTER_LINEAR)
#         title = "Warped B&W"
#         stats = None
#         self.__plot__(frame, bw_warped, 'gray', title, stats)
        
        return bw_warped
    
    def __processdownstream__(self, original, latest, data, frame):
        x_dim = latest.shape[1]
        y_dim = latest.shape[0]

        color_warp = latest

        # Warp the blank back to original image space using inverse perspective matrix (Minv)
        newwarp = cv2.warpPerspective(color_warp, self.__Minv__, (x_dim, y_dim), flags=cv2.INTER_LINEAR)
        self.__plot__(frame, Image("Warped (Original)", newwarp, None))

        # Combine the result with the original image
        unwarped = np.copy(original)
#         self.__plot__(frame, unwarped, None, "Original Color", None)
        
        title = "Unwarped Full"
        result = cv2.addWeighted(unwarped, 1, newwarp, 0.3, 0)
        self.__plot__(frame, Image(title, result, None))
         
        return result
    
    def gettransformations(self, srcvertices, destvertices):
        srcpoints = []
        destpoints = []
        for tup in srcvertices:
            if not len(tup) == 2:
                raise "Invalid # of dimensions for source point: {}".format(tup)
            [x, y] = tup
            srcpoints.append([x, y])
        
        for tup in destvertices:
            if not len(tup) == 2:
                raise "Invalid # of dimensions for dest point: {}".format(tup)
            [x, y] = tup
            destpoints.append([x, y])
        
        srcpoints = np.array([srcpoints], dtype=np.float32)
        destpoints = np.array([destpoints], dtype=np.float32)
        
        return (cv2.getPerspectiveTransform (srcpoints, destpoints), cv2.getPerspectiveTransform (destpoints, srcpoints))