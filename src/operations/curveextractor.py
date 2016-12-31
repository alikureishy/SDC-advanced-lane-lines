'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import cv2
import numpy as np
    
# Detects and fits the lane points, then fills the region between the fitted polynomials    
class CurveExtractor(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
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
