'''
Created on Dec 21, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
import cv2
from operations.colorspacer import ColorSpacer
from utils.utilities import plotboundary

class PerspectiveTransformer(Operation):
    # Config
    SrcPoints = 'SrcPoints'
    DestPoints = 'DestPoints'
    
    # Outputs:
    WarpedColor = "WarpedColor"

    def __init__(self, params):
        Operation.__init__(self, params)
        
        # Later it might be good to figure out the source/destination points automatically:
        self.__M__ = None
        self.__Minv__ = None
        self.__srcpoints__ = None
        self.__destpoints__ = None
        
        # Attempt to read static points from config:
        if ((self.SrcPoints in params) & (self.DestPoints in params)):
            self.__srcpoints__, self.__destpoints__ = params[self.SrcPoints], params[self.DestPoints]
            self.__M__, self.__Minv__ = self.gettransformations(params[self.SrcPoints], params[self.DestPoints])
        else:
            raise "Source and/or destination points not provided for perspective transformation"

    def __processupstream__(self, original, latest, data, frame):
        x_dim = latest.shape[1]
        y_dim = latest.shape[0]

        # Obtain the perspective and transform points:
        

        # Plot the source points, for the benefit of the viewer
        if self.isplotting():
            # Show perspective regions:
            orig = np.copy(self.getdata(data, self.Upstream, ColorSpacer))
            plotboundary(orig, self.__srcpoints__, (127, 255, 212))
            self.__plot__(frame, orig, None, "Warp Region (Source)", None)

            # Show warped original:
            orig = np.copy(self.getdata(data, self.Upstream, ColorSpacer))
            warped_orig = cv2.warpPerspective(orig, self.__M__, (x_dim, y_dim), flags=cv2.INTER_LINEAR)
            plotboundary(warped_orig, self.__destpoints__, (255, 192, 203))
            self.__plot__(frame, warped_orig, None, "Warped (Original)", None)
            self.setdata(data, self.WarpedColor, warped_orig)

        # Perform perspective transform:
        bw_warped = cv2.warpPerspective(np.float32(latest), self.__M__, (x_dim, y_dim), flags=cv2.INTER_LINEAR)
        title = "Warped B&W"
        stats = None
        self.__plot__(frame, bw_warped, 'gray', title, stats)
        
        return bw_warped
    
    def __processdownstream__(self, original, latest, data, frame):
        x_dim = latest.shape[1]
        y_dim = latest.shape[0]

        color_warp = latest

        # Warp the blank back to original image space using inverse perspective matrix (Minv)
        newwarp = cv2.warpPerspective(color_warp, self.__Minv__, (x_dim, y_dim), flags=cv2.INTER_LINEAR)
        # Combine the result with the original image
        undist = self.getdata(data, ColorSpacer.Upstream, ColorSpacer)
        result = cv2.addWeighted(undist, 1, newwarp, 0.3, 0)

        title = "Unwarped"
        stats = None
        self.__plot__(frame, result, None, title, stats)
         
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