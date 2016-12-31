'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
import cv2

# Detects the points on each lane and fits each with a polynomial function
# Also detects the position of the car relative to the center of the lane,
# based on the lane positions.
class LaneFinder(Operation):
#     NumSlices = "NumSlices" # Should be at least 3
    LeftLane = "LeftLane"
    RightLane = "RightLane"
    
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
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

        # Prepare the lanes for subsequent processing upstream:
        leftlane = Lane(yvals, leftx, left_fit, left_fitx)
        rightlane = Lane(yvals, rightx, right_fit, right_fitx)
        self.setdata(data, self.LeftLane, leftlane)
        self.setdata(data, self.RightLane, rightlane)

        return latest
    
    def blah(self):
        
        x_dim, y_dim = latest.shape[1], latest.shape[0]
        
        numslices = self.getparam(self.NumSlices)
        slicesize = int(y_dim / numslices)
        
        # Get a histogram of each horizontal slice and find peaks
        # Assumption is that the center of the center of the camera
        # is always soewhere between the left and right lanes.
        binary = np.array(latest).astype(bool)
        histimage = np.zeros_like(latest)
        leftbucket = []
        rightbucket = []
        for i in range(numslices):
            start, end = i*slicesize, min((i*slicesize)+slicesize, len(latest))
            histogram = np.sum(binary[start:end,:], axis=0)

            # Determine the position of the two lanes:
            center = int(x_dim / 2)
            leftpeaks = self.findpeaks(histogram[0:center]).reverse() # [(x, strength)]
            rightpeaks = self.findpeaks(histogram[center:]) # [(x, strength)]
            leftbucket.append(leftpeaks)
            rightbucket.append(rightpeaks)
            
            if self.isplotting():
                points = np.int32(list(zip(list(range(0, x_dim)), y_dim - histogram)))
                cv2.polylines(histimage, [points], False, 255, 5)


        # Calculate lines:
        

        if self.isplotting():
            self.__plot__(frame, histimage, 'gray', "Histogram", None)
        
        return latest

def findpeaks(distribution):
    peaks = []
    

class Lane(object):
    def __init__(self, yvals, xs, fit, fitx):
        self.yvals = yvals
        self.xs = xs
        self.fit = fit
        self.fitx = fitx
    

# Define a class to receive the characteristics of each line detection
class Line1():
    def __init__(self):
        # was the line detected in the last iteration?
        self.detected = False  
        # x values of the last n fits of the line
        self.recent_xfitted = [] 
        #average x values of the fitted line over the last n iterations
        self.bestx = None     
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = None  
        #polynomial coefficients for the most recent fit
        self.current_fit = [np.array([False])]  
        #radius of curvature of the line in some units
        self.radius_of_curvature = None 
        #distance in meters of vehicle center from the line
        self.line_base_pos = None 
        #difference in fit coefficients between last and new fits
        self.diffs = np.array([0,0,0], dtype='float') 
        #x values for detected line pixels
        self.allx = None  
        #y values for detected line pixels
        self.ally = None