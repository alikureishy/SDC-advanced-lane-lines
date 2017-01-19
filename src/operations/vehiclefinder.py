'''
Created on Jan 14, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from sklearn.externals import joblib
from extractors.colorhistogram import ColorHistogram
from extractors.spatialbinner import SpatialBinner
from extractors.hogextractor import HogExtractor
from extractors.featurecombiner import FeatureCombiner
from statistics import mean
import numpy as np
from utils.utilities import getperspectivepoints
import cv2
from extractors.helper import buildextractor



class VehicleFinder(Operation):
    ClassifierFile = 'ClassifierFile'
    FeatureExtractors = 'FeatureExtractors'
    SlidingWindow = 'SlidingWindow'
    class SlidingWindow(object):
        DepthRangeRatio = 'DepthRangeRatio'
        DefaultHeadingRatios = 'DefaultHeadingRatios'
        CenterShiftRatio = 'CenterShiftRatio'
        SizeVariations = 'SizeVariations'
        WindowRangeRatio = 'WindowRangeRatio'
        StepRatio = 'StepRatio'
        ConfidenceThreshold = 'ConfidenceThreshold'

    # Constants:
    AllWindowColor = [152, 0, 0]
    WeakWindowColor = [200, 0, 0]
    StrongWindowColor = [255, 0, 0]

    # Outputs
    FrameVehicleDetections = "FrameVehicleDetections"

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__classifier__ = joblib.load(params[self.ClassifierFile])
        self.__windows__ = None
        
        # Feature Extractors
        extractorsequence = params[self.FeatureExtractors]
        self.__feature_extractor__ = buildextractor(extractorsequence)
        
        self.__frame_vehicles__ = None

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim, xy_avg = latest.shape[1], latest.shape[0], int(mean(latest.shape[0:2]))
        slidingwindowconfig = self.getparam(self.SlidingWindow.__name__)
        if self.__windows__ is None:
            self.__confidence_threshold__ = slidingwindowconfig[self.SlidingWindow.ConfidenceThreshold]
            self.__windows__ = self.generatewindows(slidingwindowconfig, x_dim, y_dim, xy_avg)

        # Perform search:
        image = np.copy(latest)
        weak_candidate_vehicles = []
        strong_candidate_vehicles = []
        for scan in self.__windows__:
            for (x1, x2, y1, y2) in scan:
                window = image[y1:y2,x1:x2,:]
                features = self.__feature_extractor__.extract(window)
                sample = features.reshape(1, -1)
                label = self.__classifier__.predict(sample)
                score = self.__classifier__.decision_function(sample)
#                 print ("Score obtained: {}".format(score))
                if label == 1:
                    weak_candidate_vehicles.append((x1,x2,y1,y2))
                if score > self.__confidence_threshold__:
                    strong_candidate_vehicles.append((x1,x2,y1,y2))
        self.__frame_vehicles__ = strong_candidate_vehicles
        self.setdata(data, self.FrameVehicleDetections, self.__frame_vehicles__)

        if self.isplotting():
            # First show all windows being searched:
            image_all = np.zeros_like(latest)
            for scan in self.__windows__:
                for (x1,x2,y1,y2) in scan:
                    cv2.rectangle(image_all, (x1,y1), (x2,y2), self.AllWindowColor, 3)
                    
            # Then show all windows that were weak candidates:            
            images_weak = np.copy(latest)
            for (x1,x2,y1,y2) in weak_candidate_vehicles:
                cv2.rectangle(images_weak, (x1,y1), (x2,y2), self.WeakWindowColor, 4)
            todraw = cv2.addWeighted(images_weak, 0.8, image_all, 0.4, 0)

            # Then show all windows that were strong candidates:
            image_strong = np.copy(latest)
            for (x1,x2,y1,y2) in strong_candidate_vehicles:
                cv2.rectangle(image_strong, (x1,y1), (x2,y2), self.StrongWindowColor, 5)
            todraw = cv2.addWeighted(image_strong, 1, image_all, 0.4, 0)
            self.__plot__(frame, todraw, None, "Vehicle Search & Hits (Weak/Strong = {}/{})".format(len(weak_candidate_vehicles), len(strong_candidate_vehicles)), None)
            
        return latest

    def getboxcorners(self, center, size, xrange, yrange):
        if center[0] <= xrange[0] or center[0] >= xrange[1]:
#             print ("Warning: Attempt to generate windows around overflowing center: {} with size: {}".format(center, size))
            return None
        if center[1] <= yrange[0] or center[1] >= yrange[1]:
#             print ("Warning: Attempt to generate windows around overflowing center: {} with size: {}".format(center, size))
            return None
        
        s = int(size/2)
        x = center[0]
        y = center[1]
        
        leftx = x-s
        rightx = x+s
        topy = y-s
        bottomy = y+s
        if leftx < xrange[0]:
            leftx = xrange[0]
        if rightx > xrange[1]:
            rightx = xrange[1]
        if topy < yrange[0]:
            topy = yrange[0]
        if bottomy > yrange[1]:
            bottomy = yrange[1]
            
        assert not (leftx == rightx) or not (topy == bottomy), "Zero sized window found with center: {}, size: {}".format(center, size)
        return (leftx, rightx, topy, bottomy)
    
    def generatewindows(self, cfg, x_dim, y_dim, xy_avg):
        shift = cfg[self.SlidingWindow.CenterShiftRatio] * x_dim
        depth_range_ratio = sorted(cfg[self.SlidingWindow.DepthRangeRatio], reverse=True)
        horizon = min([int(y_dim * r) for r in depth_range_ratio])
        print ("Horizon is at depth: {}".format(horizon))
        window_range_ratio = cfg[self.SlidingWindow.WindowRangeRatio]
        window_range = [int(xy_avg * r) for r in window_range_ratio]
        print ("Window range: {}".format(window_range))
        size_variations = cfg[self.SlidingWindow.SizeVariations]
        grow_rate = int(np.absolute(window_range[1]-window_range[0])/(size_variations))
        print ("Window grow rate (each side): {}".format(grow_rate))
        slide_ratio = cfg[self.SlidingWindow.StepRatio]
        center = (int((x_dim / 2) + shift), horizon)
        print ("Center of vision: {}".format(center))
        
        windows = []
        for i in range(size_variations):
            print ("Scan # {}".format(i))
            windows.append([])
            scanwidth = int(x_dim/2)
            print ("\tScan width: {}".format(scanwidth))
            boxwidth = window_range[0] + (i * grow_rate)
            print ("\tBox width: {}".format(boxwidth))
            center_box = self.getboxcorners(center, boxwidth, [0, x_dim], [0, y_dim])
            if center_box is None:
                print ("\tCenter box (OUTSIDE BOUNDS): {}".format(center_box))
                continue
            print ("\tCenter box: {}".format(center_box))
            windows[i].append(center_box)
            shifts_per_box = int(1 / slide_ratio)
            boxshift = int(boxwidth * slide_ratio)
            print ("\t\tBox shift: {}".format(boxshift))
            numboxes = int(scanwidth / boxwidth) # Boxes each side of the center box
            print ("\t\tNum boxes: {}".format(numboxes))
            # Each box on left + right sides of center:
            print ("\t\t\tShifts Per Box: {}".format(shifts_per_box))
            for j in range(1, numboxes + 1):
                print ("\t\t\tShifted Boxes # ({})".format('~'*j))
                for k in range(0, shifts_per_box):
                    leftcenter = (center[0] - (j * boxwidth) - (k * boxshift), center[1])
                    left_box = self.getboxcorners(leftcenter, boxwidth, [0, x_dim], [0, y_dim])
                    rightcenter = (center[0] + (j * boxwidth) + (k * boxshift), center[1])
                    right_box = self.getboxcorners(rightcenter, boxwidth, [0, x_dim], [0, y_dim])
                    if left_box is None or right_box is None:
                        continue
                    windows[i].append(left_box)
                    windows[i].append(right_box)
                    print ("\t\t\t\tShift # {}: <--{} {} {}-->".format(k, left_box, '~'*(k+1), right_box))
            print ("\tTotal boxes in scan: {}".format(len(windows[i])))
        return windows

