'''
Created on Dec 31, 2016

@author: safdar
'''
import cv2
import numpy as np
import math

class HoughFilterParams(object):
    _ = 'HoughFilter'
    Rho = 'Rho'
    Theta = 'Theta'
    Threshold = 'Threshold'
    MinLineLength = 'MinLineLength'
    MaxLineGap = 'MaxLineGap'
    LeftRadianRange = 'LeftRadianRange'
    RightRadianRange = 'RightRadianRange'
    DepthRangeRatio = 'DepthRangeRatio'

def plotboundary(orig, points, color):
    topleft = tuple(points[0])
    topright = tuple(points[1])
    bottomleft = tuple(points[2])
    bottomright = tuple(points[3])
    cv2.line(orig, topleft, topright, color, 7)
    cv2.line(orig, topright, bottomright, color, 7)
    cv2.line(orig, bottomright, bottomleft, color, 7)
    cv2.line(orig, bottomleft, topleft, color, 7)

def drawlines(image, lines, color=100, thickness=10):
    if not lines is None:
        for line in lines:
            if not line is None:
                for x1,y1,x2,y2 in line:
                    cv2.line(image, (x1, y1), (x2, y2), color, thickness)
    return image

def extractlanes(image, filterparams):
    rho = filterparams[HoughFilterParams.Rho]
    theta = filterparams[HoughFilterParams.Theta]
    threshold = filterparams[HoughFilterParams.Threshold]
    min_line_len = filterparams[HoughFilterParams.MinLineLength]
    max_line_gap = filterparams[HoughFilterParams.MaxLineGap]
    left_radian_range = filterparams[HoughFilterParams.LeftRadianRange]
    right_radian_range = filterparams[HoughFilterParams.RightRadianRange]
    depth_range_ratios = filterparams[HoughFilterParams.DepthRangeRatio]
    
    x_dim, y_dim = image.shape[1], image.shape[0]
    depth_range = [y_dim*depth_range_ratios[0], y_dim*depth_range_ratios[1]]
    y_min = max(depth_range)
    y_max = min(depth_range)
    
    lines = cv2.HoughLinesP(np.uint8(image), rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)

    # Additional processing:
    if lines is not None:
        # Buckets
        leftlanelines = []
        leftslope = 0
        rightlanelines = []
        rightslope = 0
        badlines = []
        leftlanerange = left_radian_range #[-0.90, -0.55]
        rightlanerange = right_radian_range  #[0.55, 0.90]
        leftmetrics = [0, 0, 0]    # cumulative [slope, intercept]
        rightmetrics = [0, 0, 0]   # cumulative [slope, intercept]
        for line in lines:
            #print (line)
            # Calculate metrics and bucket:
            slope = 0
            line_rad = 0
            x_1 = line[0][0]
            x_2 = line[0][2]
            y_1 = line[0][1]
            y_2 = line[0][3]
            delta_x = float(x_2 - x_1)
            delta_y = float(y_2 - y_1) #Since the y axis is inverted
            if not delta_x == 0:
                length = math.sqrt (delta_x**2 + delta_y**2)
                slope = delta_y / delta_x
                line_rad = math.tan(slope)
                intercept = (y_1 - (slope * x_1))

                # Determine quadrant
                if leftlanerange[0] <= line_rad <= leftlanerange[1]:
                    #print (\"Adding left...\", line, slope, intercept)
                    leftlanelines.append(line)
                    leftmetrics[0] += slope*length
                    leftmetrics[1] += intercept*length
                    leftmetrics[2] += length
                elif rightlanerange[0] <= line_rad <= rightlanerange[1]:
                    #print (\"Adding right...\", line, slope, intercept)
                    rightlanelines.append(line)
                    rightmetrics[0] += slope*length
                    rightmetrics[1] += intercept*length
                    rightmetrics[2] += length
                else:
                    badlines.append(line)

        # Process left/right lanes to find the main line:
        # Use longest line approach:
        leftlane = None
        if (not leftlanelines is None) & (len(leftlanelines) > 0):
            leftslope = leftmetrics[0]/leftmetrics[2]
            leftintercept = leftmetrics[1]/leftmetrics[2]
            #print (\"Calculating left...\", leftmetrics[0], leftmetrics[1], len(leftlanelines))
            y_1 = int(y_min)
            x_1 = int((y_1 - leftintercept) / leftslope)
            y_2 = int(y_max)
            x_2 = int((y_2 - leftintercept) / leftslope)
            leftlane = [[x_1, y_1, x_2, y_2]]

        rightlane = None
        if (not rightlanelines is None) & (len(rightlanelines) > 0):
            rightslope = rightmetrics[0]/rightmetrics[2]
            rightintercept = rightmetrics[1]/rightmetrics[2]
            #print (\"Calculating right...\", rightmetrics[0], rightmetrics[1], len(rightlanelines), rightslope, rightintercept)
            y_1 = int(y_min)
            x_1 = int((y_1 - rightintercept) / rightslope)
            y_2 = int(y_max)
            x_2 = int((y_2 - rightintercept) / rightslope)
            rightlane = [[x_1, y_1, x_2, y_2]]
    
        return lines, leftlane, rightlane
    else:
        return lines, None, None