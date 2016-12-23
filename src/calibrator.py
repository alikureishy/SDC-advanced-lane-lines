'''
Created on Dec 21, 2016

@author: safdar
'''
import argparse
import numpy as np
import cv2
import glob
import matplotlib
#matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

if __name__ == '__main__':
    print ("###############################################")
    print ("#                 CALIBRATOR                  #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Camera Calibrator')
    parser.add_argument('-i', dest='input',    required=True, type=str, help='Path to distorted image file or distorted images folder.')
    parser.add_argument('-f', dest='output',   required=True, type=str, help='Location of output (Will be treated as the same as input type)')
    parser.add_argument('-o', dest='overwrite', action='store_true', help='Overwrite output file(s) if they already exist (default: false)')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    args = parser.parse_args()






    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*8,3), np.float32)
    objp[:,:2] = np.mgrid[0:8, 0:6].T.reshape(-1,2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d points in real world space
    imgpoints = [] # 2d points in image plane.
    
    # Make a list of calibration images
    images = glob.glob('calibration_wide/GO*.jpg')
    
    # Step through the list and search for chessboard corners
    for idx, fname in enumerate(images):
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, (8,6), None)
    
        # If found, add object points, image points
        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)
    
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (8,6), corners, ret)
            #write_name = 'corners_found'+str(idx)+'.jpg'
            #cv2.imwrite(write_name, img)
            
    #         cv2.imshow('img', img)
    #         cv2.waitKey(500)
    
    cv2.destroyAllWindows()
