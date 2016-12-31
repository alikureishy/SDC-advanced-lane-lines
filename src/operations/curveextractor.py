'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
from operations.lanefinder import LaneFinder
    
# Detects and fits the lane points, then fills the region between the fitted polynomials    
class CurveExtractor(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):

        # Define conversions in x and y from pixels space to meters
        ym_per_pix = 30/720 # meters per pixel in y dimension
        xm_per_pix = 3.7/700 # meteres per pixel in x dimension
        
        leftlane = self.getdata(data, LaneFinder.LeftLane, LaneFinder)
        rightlane = self.getdata(data, LaneFinder.RightLane, LaneFinder)
        if not leftlane is None and not rightlane is None:
            yvals = leftlane.yvals
            left_fit = leftlane.fit
            leftx = leftlane.xs
            right_fit = rightlane.fit
            rightx = rightlane.xs
            
            y_eval = np.max(yvals)
    
            # Determine the curvature in pixel-space
            left_curverad_ps = ((1 + (2*left_fit[0]*y_eval + left_fit[1])**2)**1.5) \
                                 /np.absolute(2*left_fit[0])
            right_curverad_ps = ((1 + (2*right_fit[0]*y_eval + right_fit[1])**2)**1.5) \
                                            /np.absolute(2*right_fit[0])
            leftlane.curverad_ps = left_curverad_ps
            rightlane.curverad_ps = right_curverad_ps
    
            # Determine curvature in real space
            left_fit_cr = np.polyfit(yvals*ym_per_pix, leftx*xm_per_pix, 2)
            right_fit_cr = np.polyfit(yvals*ym_per_pix, rightx*xm_per_pix, 2)
            left_curverad_rs = ((1 + (2*left_fit_cr[0]*y_eval + left_fit_cr[1])**2)**1.5) \
                                         /np.absolute(2*left_fit_cr[0])
            right_curverad_rs = ((1 + (2*right_fit_cr[0]*y_eval + right_fit_cr[1])**2)**1.5) \
                                            /np.absolute(2*right_fit_cr[0])
            leftlane.curverad_rs = left_curverad_rs
            rightlane.curverad_rs = right_curverad_rs
    
        return latest