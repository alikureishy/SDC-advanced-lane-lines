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
    DriftToleranceRatio = 'DriftToleranceRatio'
    SafeColor = 'SafeColor'
    DangerColor = 'DangerColor'
    LaneConfidenceThreshold = 'LaneConfidenceThreshold'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__drift_tolerance_ratio__ = params[self.DriftToleranceRatio]
        self.__drift_tolerance_pixels__ = None
        self.__left_fitx__ = None
        self.__right_fitx__ = None
        self.__yvals__ = None
        self.__drift_pixels__ = None
        self.__drift_meters__ = None
        self.__safe_color__ = tuple(params[self.SafeColor])
        self.__danger_color__ = tuple(params[self.DangerColor])
        self.__lane_confidence_threshold__ = params[self.LaneConfidenceThreshold]

    def is_drift_safe(self, drift_ps, drift_tolerance_ps):
        return abs(drift_ps) < drift_tolerance_ps

    def __processupstream__(self, original, latest, data, frame):
        # Check if new lane information is available:
        leftlane = self.getdata(data, LaneFinder.LeftLane, LaneFinder)
        rightlane = self.getdata(data, LaneFinder.RightLane, LaneFinder)
        car = self.getdata(data, LaneFinder.Car, LaneFinder)
        
        if self.__drift_tolerance_pixels__ is None:
            self.__drift_tolerance_pixels__ = self.__drift_tolerance_ratio__ * latest.shape[1]
        
        if not leftlane is None and not rightlane is None and not car is None:
            if not leftlane.getlatestfitxs() is None and leftlane.get_totalconfidence() >= self.__lane_confidence_threshold__:
                self.__left_fitx__ = leftlane.getlatestfitxs()
            if not rightlane.getlatestfitxs() is None and rightlane.get_totalconfidence() >= self.__lane_confidence_threshold__:
                self.__right_fitx__ = rightlane.getlatestfitxs()
            self.__yvals__ = leftlane.getyvals()
            if not car.get_drift() == (None, None):
                self.__drift_pixels__, self.__drift_meters__ = car.get_drift()

        # Prepare the foreground that will be superimposed onto the main color image:
        zeros1d = np.zeros_like(latest).astype(np.uint8)
        foreground = np.dstack((zeros1d, zeros1d, zeros1d))
        if not self.__left_fitx__ is None and not self.__right_fitx__ is None and not self.__drift_pixels__ is None:
            # Recast the x and y points into usable format for cv2.fillPoly()
            pts_left = np.array([np.transpose(np.vstack([self.__left_fitx__, self.__yvals__]))])
            pts_right = np.array([np.flipud(np.transpose(np.vstack([self.__right_fitx__, self.__yvals__])))])
            pts = np.hstack((pts_left, pts_right))
            
            # Draw the lane onto the image
            shade = self.__safe_color__ if self.is_drift_safe(self.__drift_pixels__, self.__drift_tolerance_pixels__) else self.__danger_color__
            cv2.fillPoly(foreground, np.int_([pts]), shade)
#         self.__plot__(frame, foreground, 'gray', "Foreground", None)
            
        if self.isplotting():
            # Get the color image to draw the lane on, just for illustration
            color = self.getdata(data, PerspectiveTransformer.WarpedColor, PerspectiveTransformer).copy()
            color = cv2.addWeighted(color, 1, foreground, 0.4, 0)
            self.__plot__(frame, color, None, "Filled Lane", None)

        return foreground
        