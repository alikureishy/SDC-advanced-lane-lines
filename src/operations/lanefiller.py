'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
import cv2
from operations.perspective import Perspective

class LaneFiller(Operation):
    LeftFitX = 'LeftFitX'
    RightFitX = 'RightFitX'
    
    
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        warped = latest
        
        # Generate some fake data to represent lane-line pixels
        yvals = np.linspace(0, 100, num=101)*7.2  # to cover same y-range as image
        leftx = np.array([200 + (elem**2)*4e-4 + np.random.randint(-50, high=51) \
                                      for idx, elem in enumerate(yvals)])
        leftx = leftx[::-1]  # Reverse to match top-to-bottom in y
        rightx = np.array([900 + (elem**2)*4e-4 + np.random.randint(-50, high=51) \
                                        for idx, elem in enumerate(yvals)])
        rightx = rightx[::-1]  # Reverse to match top-to-bottom in y
        
        # Fit a second order polynomial to each fake lane line
        left_fit = np.polyfit(yvals, leftx, 2)
        left_fitx = left_fit[0]*yvals**2 + left_fit[1]*yvals + left_fit[2]
        right_fit = np.polyfit(yvals, rightx, 2)
        right_fitx = right_fit[0]*yvals**2 + right_fit[1]*yvals + right_fit[2]

        # Get the warped color image to draw the lane on:
        warp_zero = np.zeros_like(warped).astype(np.uint8)
        layer_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        
        # Recast the x and y points into usable format for cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([left_fitx, yvals]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, yvals])))])
        pts = np.hstack((pts_left, pts_right))
        
        # Draw the lane onto the warped blank image
        cv2.fillPoly(layer_warp, np.int_([pts]), (0,255, 0))
        
        if self.isplotting():
            # Get the warped color image to draw the lane on:
            color_warp = self.getdata(data, Perspective.WarpedColor, Perspective).copy()
            color_warp = cv2.addWeighted(color_warp, 1, layer_warp, 0.3, 0)
            self.__plot__(frame, color_warp, None, "MarkedLane", None)
        
        return layer_warp
        