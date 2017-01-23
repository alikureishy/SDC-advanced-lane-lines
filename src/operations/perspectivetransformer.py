'''
Created on Dec 21, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
import cv2
from utils.plotter import Image
from utils.utilities import plotboundary, getperspectivepoints

# Default:
#  Left ds = (.26*x, -.33*y) = (332, -237)
#  Right ds = (-.32*x, -.33*y) = (x_dim-409, -237)

class PerspectiveTransformer(Operation):
    # Config
    Perspective = 'Perspective'
    DepthRangeRatio = 'DepthRangeRatio'
    TransformRatios = 'TransformRatios'
    
    # Outputs:
    WarpedColor = "WarpedColor"

    def __init__(self, params):
        Operation.__init__(self, params)
        
        self.__M__ = None
        self.__Minv__ = None
        self.__perspective__ = params[self.Perspective]
        self.__depth_range_ratios__ = params[self.DepthRangeRatio]
        self.__transform_ratios__ = params[self.TransformRatios]
        self.__perspective_points__ = None
        self.__transform_points__ = None
        
    def __processupstream__(self, original, latest, data, frame):
        x_dim = latest.shape[1]
        y_dim = latest.shape[0]

        # Calculate and cache the transform and perspective points since these will never change:
        if self.__transform_points__ is None:
            self.__perspective_points__ = getperspectivepoints(x_dim, y_dim, self.__depth_range_ratios__, self.__perspective__)
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