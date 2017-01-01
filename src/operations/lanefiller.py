'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
import cv2
from operations.perspectivetransformer import PerspectiveTransformer
from operations.lanefinder import LaneFinder

class LaneFiller(Operation):
    LeftFitX = 'LeftFitX'
    RightFitX = 'RightFitX'
    
    
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        
        result = latest
        
        # Obtain the data from the LaneFinder handler's output
        leftlane = self.getdata(data, LaneFinder.LeftLane, LaneFinder)
        rightlane = self.getdata(data, LaneFinder.RightLane, LaneFinder)
        
        if not leftlane is None and not rightlane is None:
            left_fitx = leftlane.fitx
            right_fitx = rightlane.fitx
            yvals = leftlane.yvals
    
            # Recast the x and y points into usable format for cv2.fillPoly()
            pts_left = np.array([np.transpose(np.vstack([left_fitx, yvals]))])
            pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, yvals])))])
            pts = np.hstack((pts_left, pts_right))
            
            # Create a background onto which to draw the warped lane polygon:
            warped = latest
            warp_zero = np.zeros_like(warped).astype(np.uint8)
            layer_warp = np.dstack((warp_zero, warp_zero, warp_zero))
            
            # Draw the lane onto the warped blank image
            cv2.fillPoly(layer_warp, np.int_([pts]), (0,255, 0))
            result = layer_warp
            
            if self.isplotting():
                # Get the warped color image to draw the lane on:
                color_warp = self.getdata(data, PerspectiveTransformer.WarpedColor, PerspectiveTransformer).copy()
                color_warp = cv2.addWeighted(color_warp, 1, layer_warp, 0.3, 0)
                self.__plot__(frame, color_warp, None, "MarkedLane", None)

        return result
        