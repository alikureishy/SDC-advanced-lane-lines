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
    
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
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
    

class LineBuilder(object):
    pass

# Define a class to receive the characteristics of each line detection
class Line():
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