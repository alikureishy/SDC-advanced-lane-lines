'''
Created on Dec 21, 2016

@author: safdar
'''
import argparse
import numpy as np
import cv2
import glob
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import os
import pickle

if __name__ == '__main__':
    print ("###############################################")
    print ("#                 CALIBRATOR                  #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Camera Calibrator')
    parser.add_argument('-i', dest='input',    required=True, type=str, help='Path to folder containing calibration images.')
    parser.add_argument('-o', dest='output',   required=True, type=str, help='Location of output (Will be treated as the same as input type)')
    parser.add_argument('-s', dest='size', default = (9, 6), help='Size of the checkboard : (horizontal, vertical)')
    parser.add_argument('-t', dest='test', type=str, help='Test file to undistort for visual verification.')
    parser.add_argument('-p', dest='plot', action='store_true', help='Plot the chessboard with dots drawn (default: false).')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    
    args = parser.parse_args()

    # Make a list of calibration images
    if not os.path.isdir(args.input):
        raise "Folder does not exist, or is not a folder: {}".format(args.input)
    
    images = glob.glob(os.path.join(args.input, '*.jpg'))
    assert len(images)>0, "There should be at least one image to process. Found 0."

    h = args.size[0]
    v = args.size[1]

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros(((h*v), 3), np.float32)
    objp[:,:2] = np.mgrid[0:h, 0:v].T.reshape(-1,2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d points in real world space
    imgpoints = [] # 2d points in image plane.
    
    # Step through the list and search for chessboard corners
    for idx, fname in enumerate(images):
        image = cv2.imread(fname)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, (h,v), None)
    
        # If found, add object points, image points
        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)
    
            # Draw and display the corners
            if (args.plot):
                cv2.drawChessboardCorners(image, (h,v), corners, ret)
#                 write_name = 'corners_found'+str(idx)+'.jpg'
#                 cv2.imwrite(write_name, image)
                cv2.imshow('image', image)
                cv2.waitKey(500)
                
    if (args.plot):
        cv2.destroyAllWindows()

    # Do camera calibration given object points and image points
    sample = cv2.imread(images[0])
    img_size = (sample.shape[1], sample.shape[0])
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_size,None,None)

    if not args.dry:
        print ("Saving checkpoints to file: {}".format(args.output))
        dist_pickle = {}
        dist_pickle["mtx"] = mtx
        dist_pickle["dist"] = dist
        pickle.dump( dist_pickle, open( args.output, "wb" ) )

    if not args.test==None:
        if not os.path.isfile(args.test):
            raise "Test image file does not exist: {}".format(args.test)
        
        test_image = cv2.imread(args.test)
        img_size = (test_image.shape[1], test_image.shape[0])
        undistorted = cv2.undistort(test_image, mtx, dist, None, mtx)
        f, (ax1, ax2) = plt.subplots (1, 2, figsize=(20,10))
        ax1.imshow(test_image)
        ax1.set_title('Original Image', fontsize=30)
        ax2.imshow(undistorted)
        ax2.set_title('Undistorted Image', fontsize=30)
        plt.show()

    print ("Thank you. Come again!")
