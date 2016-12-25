'''
Created on Dec 20, 2016

@author: safdar
'''

import numpy as np
import cv2
import matplotlib
import enum
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Define a function that applies Sobel x or y, 
# then takes an absolute value and applies a threshold.
# Note: calling your function with orient='x', thresh_min=5, thresh_max=100
# should produce output like the example image shown above this quiz.
def abs_sobel_thresh(image, orient='x', sobel_kernel=3, thresh=(0, 255)):

    gray = None
    if len(image.shape)<3:
        gray = image
    elif image.shape[2]<3:
        gray = image
    else:
        # Apply the following steps to image
        # 1) Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2) Take the derivative in x or y given orient = 'x' or 'y'
    sobel = None
    if orient == 'x':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
    elif orient == 'y':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel)
    else:
        raise "Invalid orientation provided: {}".format(orient)

    # 3) Take the absolute value of the derivative or gradient
    abs_sobel = np.absolute(sobel)
    
    # 4) Scale to 8-bit (0 - 255) then convert to type = np.uint8
    scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
    
    # 5) Create a mask of 1's where the scaled gradient magnitude 
            # is > thresh_min and < thresh_max
    binary_sobel = np.zeros_like(scaled_sobel)
    binary_sobel[(scaled_sobel > thresh[0]) & (scaled_sobel <= thresh[1])] = 1
    
    # 6) Return this mask as your binary_output image
    binary_output = np.copy(binary_sobel)
    return binary_output
    
# Define a function that applies Sobel x and y, 
# then computes the magnitude of the gradient
# and applies a threshold
def mag_thresh(image, sobel_kernel=3, mag_thresh=(0, 255)):
    
    gray = None
    if len(image.shape)<3:
        gray = image
    elif image.shape[2]<3:
        gray = image
    else:
        # Apply the following steps to image
        # 1) Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2) Take the gradient in x and y separately
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel)

    # 3) Calculate the magnitude
    abs_sobel = np.sqrt(sobelx**2 + sobely**2)
    
    # 5) Scale to 8-bit (0 - 255) and convert to type = np.uint8
    scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
    
    # 6) Create a binary mask where mag thresholds are met
    binary_sobel = np.zeros_like(scaled_sobel)
    binary_sobel[(scaled_sobel > mag_thresh[0]) & (scaled_sobel < mag_thresh[1])] = 1
        
    # 7) Return this mask as your binary_output image
    binary_output = np.copy(binary_sobel)
    return binary_output

# Define a function that applies Sobel x and y, 
# then computes the direction of the gradient
# and applies a threshold.
def dir_threshold(image, sobel_kernel=3, thresh=(0, np.pi/2)):
    
    gray = None
    if len(image.shape)<3:
        gray = image
    elif image.shape[2]<3:
        gray = image
    else:
        # Apply the following steps to image
        # 1) Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2) Take the gradient in x and y separately
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel)

    # 3) Take the absolute value of the x and y gradients
    abs_sobelx = np.absolute(sobelx)
    abs_sobely = np.absolute(sobely)
    
    # 4) Use np.arctan2(abs_sobely, abs_sobelx) to calculate the direction of the gradient
    tan_sobel = np.arctan2(abs_sobely, abs_sobelx)

    # 5) Create a binary mask where direction thresholds are met
    binary_sobel = np.zeros_like(tan_sobel)
    binary_sobel[(tan_sobel > thresh[0]) & (tan_sobel < thresh[1])] = 1
    
    # 6) Return this mask as your binary_output image
    binary_output = np.copy(binary_sobel) # Remove this line
    return binary_output

class Space(Enum):
    hls = cv2.COLOR_BGR2HLS
    hsv = cv2.COLOR_BGR2HSV

class HLS(Enum):
    Hue = 0
    Lightness = 1
    Saturation = 2

class Gray(Enum):
    Gray = None
    
class HSV(Enum):
    Hue = 0
    Saturation = 1
    Value = 2

class RGB(Enum):
    Red = 0
    Green = 1
    Blue = 2

def color_threshold (image, target_metric, thresh=(0,255)):
    assert not target_metric is None, "Target metric must be provided"

    mask = None
    
    if isinstance(target_metric, HLS):
        if len(image.shape)<3 | image.shape[2]<3:
            raise "Image provided with shape {} cannot be used to extract target {}".format(image.shape, target_metric.name)
        hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        idx = target_metric.value
        mask = hls[:,:,idx]
    elif isinstance(target_metric, HSV):
        if len(image.shape)<3 | image.shape[2]<3:
            raise "Image provided with shape {} cannot be used to extract target {}".format(image.shape, target_metric.name)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        idx = target_metric.value
        mask = hsv[:,:,idx]
    elif isinstance(target_metric, RGB):
        if len(image.shape)<3 | image.shape[2]<3:
            raise "Image provided with shape {} cannot be used to extract target {}".format(image.shape, target_metric.name)
        rgb = image
        idx = target_metric.value
        mask = rgb[:,:,idx]
    elif isinstance(target_metric, Gray):
        if len(image.shape)==3 & image.shape[2]==3:
            mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            mask = image
    else:
        raise "Unrecognized target metric: {}".format(target_metric)
    
    # Scale to 8-bit (0 - 255) and convert to type = np.uint8
    mask = np.absolute(mask)
    if (np.max(mask) > 255):
        mask = np.uint8(255*mask/np.max(mask))

    binary = np.zeros_like(mask)
    binary[(mask > thresh[0]) & (mask < thresh[1])] = 1

    # Bitwise-AND mask and original image
    # res = cv2.bitwise_and(frame,frame, mask= mask)
                                           
    return binary

def combined_threshold(image, sobel_settings={}):
    raise "Not implemented yet"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    outputs = []
    for key, setting in sobel_settings.iteritems():
        if key == 'direction':
            return None
        elif key == 'magnitude':
            return None
        elif key == 'x' or key == 'y':
            return None
        else:
            raise "Sobel setting not recognized: {}".format(key)
    
    combined = np.zeros_like(gray)
#    combined[((gradx == 1) & (grady == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1    
    
    return None

# Lablacian:
# laplacian = cv2.Laplacian(image,cv2.CV_64F)
