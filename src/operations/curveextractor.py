'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import cv2
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
        yvals = leftlane.yvals
        left_fit = leftlane.fit
        leftx = leftlane.xs
        right_fit = rightlane.fit
        rightx = rightlane.xs
        
        y_eval = np.max(yvals)

        # Determine the curvature in pixel-space
        left_curverad = ((1 + (2*left_fit[0]*y_eval + left_fit[1])**2)**1.5) \
                             /np.absolute(2*left_fit[0])
        right_curverad = ((1 + (2*right_fit[0]*y_eval + right_fit[1])**2)**1.5) \
                                        /np.absolute(2*right_fit[0])
        print(left_curverad, right_curverad)

        # Determine curvature in real space
        left_fit_cr = np.polyfit(yvals*ym_per_pix, leftx*xm_per_pix, 2)
        right_fit_cr = np.polyfit(yvals*ym_per_pix, rightx*xm_per_pix, 2)
        left_curverad = ((1 + (2*left_fit_cr[0]*y_eval + left_fit_cr[1])**2)**1.5) \
                                     /np.absolute(2*left_fit_cr[0])
        right_curverad = ((1 + (2*right_fit_cr[0]*y_eval + right_fit_cr[1])**2)**1.5) \
                                        /np.absolute(2*right_fit_cr[0])

        # Now our radius of curvature is in meters
        print(left_curverad, 'm', right_curverad, 'm')
        # Example values: 3380.7 m    3189.3 m        
    
        return latest

    
    def blah(self):
        
        assert len(latest.shape)<3, "Must pass a grayscale image as input into CurveExtractor"
        
        x_dim, y_dim = latest.shape[1], latest.shape[0]
        
        # detect circles in the image
        gray = np.uint8(latest.copy())
        
        # Draw test circle
#         cv2.circle(gray, (640, 360), 50, (255,255,255), 10)
#         canny = cv2.Canny(gray, 50, 150)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 3, 50, param1=100, param2=20, minRadius=700, maxRadius=2000)
        print (circles.shape)
        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
#             circles = np.round(circles[0, :]).astype("int")
         
            # loop over the (x, y) coordinates and radius of the circles
            print (type(circles))
            print ("Found {} circles...".format(len(circles)))
            for (x, y, r) in circles[0][0:3]:
                print ("Radius of curvature: {}, Center: ({}, {})".format(r,-x,y_dim-y))
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(gray, (x_dim-int(x), y_dim-int(y)), r, (128, 100, 55), 30)
#                 cv2.rectangle(gray, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        self.__plot__(frame, gray, 'gray', "Circles", None)
            
            
        return latest
