'''
Created on Dec 21, 2016

@author: safdar
'''
import matplotlib
# matplotlib.use('TKAgg')
matplotlib.use('TKAgg')
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import numpy as np
import cv2
from plotter import plot_multiple

# Import everything needed to edit/save/watch video clips
from moviepy.editor import VideoFileClip
from IPython.display import HTML

from threshold import dir_threshold, abs_sobel_thresh, mag_thresh,\
    color_threshold, RGB

def process_thresholding (image):
    # Run the functions
#     image = dir_binary = dir_threshold(image, sobel_kernel=15, thresh=(0.7, 1.3))
#     image = grad_binary = abs_sobel_thresh(image, orient='x', thresh=(20, 100))
#     image = mag_binary = mag_thresh(image, sobel_kernel=3, mag_thresh=(30, 100))
#     image = r_binary = color_threshold(image, RGB.Red, (200, 255))
    
#     plot_multiple(*((image, "Original", None),\
#                   (grad_binary, "Gradient Threshold", 'gray'),\
#                   (mag_binary, "Magnitude Threshold", 'gray'),\
#                   (dir_binary, "Direction Threshold", 'gray'),\
#                   (r_binary, "Red Threshold", 'gray')))

    return image

# Workflow
# 2 utilities:
#    - Calibrator
#    - LaneFinder
#        - Individual image input
#        - Folder of images input
#        - Video input

if __name__ == '__main__':

#     image = mpimg.imread('test_images/solidWhiteRight.jpg')
#     image = dir_binary = dir_threshold(image, sobel_kernel=15, thresh=(0.7, 1.3))
#     image = grad_binary = abs_sobel_thresh(image, orient='x', thresh=(20, 100))
#     image = mag_binary = mag_thresh(image, sobel_kernel=3, mag_thresh=(30, 100))
#     image = r_binary = color_threshold(image, RGB.Red, (200, 255))
#     plot_multiple((image, "Title", 'gray'))
    
    input_file = 'challenge_video.mp4'
    cap = cv2.VideoCapture(input_file)
    i = 0
    while(cap.isOpened()):
        ret, image = cap.read()
        if not ret:
            break
#         image = dir_binary = dir_threshold(image, sobel_kernel=15, thresh=(0.7, 1.3))
        image = grad_binary = abs_sobel_thresh(image, orient='x', thresh=(20, 100))
    #     image = mag_binary = mag_thresh(image, sobel_kernel=3, mag_thresh=(30, 100))
#         image = r_binary = color_threshold(image, RGB.Red, (200, 255))
        print("{}: {}".format(i, (image==0).sum()))
        cv2.imshow ('frame', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
#         plot_multiple((image, "Title", 'gray'))
        i+=1
         
    cap.release()
    cv2.destroyAllWindows()