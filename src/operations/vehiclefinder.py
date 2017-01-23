'''
Created on Jan 14, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from sklearn.externals import joblib
from statistics import mean
import numpy as np
from utils.utilities import getperspectivepoints
import cv2
from extractors.helper import buildextractor
import os
from utils.plotter import Image
import datetime
import PIL
import time
from sklearn.preprocessing.data import StandardScaler


class VehicleFinder(Operation):
    ClassifierFile = 'ClassifierFile'
    FeatureExtractors = 'FeatureExtractors'
    SlidingWindow = 'SlidingWindow'
    class Logging(object):
        LogHits = 'LogHits'
        LogMisses = 'LogMisses'
        FrameRange = 'FrameRange'
        Frames = 'Frames'
        LogFolder = 'LogFolder'
    class SlidingWindow(object):
        DepthRangeRatio = 'DepthRangeRatio'
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
        loggingcfg = params[self.Logging.__name__]
        self.__is_logging_hits__ = loggingcfg[self.Logging.LogHits]
        self.__is_logging_misses__ = loggingcfg[self.Logging.LogMisses]
        self.__log_folder__ = os.path.join(loggingcfg[self.Logging.LogFolder], time.strftime('%m-%d-%H-%M-%S'))
        self.__hits_folder__ = os.path.join(self.__log_folder__, 'Hits')
        self.__misses_folder__ = os.path.join(self.__log_folder__, 'Misses')
        self.__frames_to_log__ = loggingcfg[self.Logging.Frames]
        self.__frame_range_to_log__ = loggingcfg[self.Logging.FrameRange]
        
        if self.__is_logging_hits__:
            if not os.path.isdir(self.__hits_folder__):
                os.makedirs(self.__hits_folder__, exist_ok=True)
        if self.__is_logging_misses__:
            if not os.path.isdir(self.__misses_folder__):
                os.makedirs(self.__misses_folder__, exist_ok=True)
        
        # Feature Extractors
        extractorsequence = params[self.FeatureExtractors]
        self.__feature_extractor__ = buildextractor(extractorsequence)
        
        self.__frame_vehicles__ = None
        self.__frame_counter__ = 0

    def islogginghits(self):
        return self.__is_logging_hits__==1

    def isloggingmisses(self):
        return self.__is_logging_misses__==1

    def isframewithrange(self):
        return self.__frame_counter__ in range(*self.__frame_range_to_log__) or \
            self.__frame_counter__ in self.__frames_to_log__

    def log(self, folder, window, i, j):
        if self.isframewithrange():
            windowdumpfile = os.path.join(folder, "{:04d}_{:02d}_{:02d}.png".format(self.__frame_counter__, i, j))
            towrite = PIL.Image.fromarray(window)
            towrite.save(windowdumpfile)

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim, xy_avg = latest.shape[1], latest.shape[0], int(mean(latest.shape[0:2]))
        slidingwindowconfig = self.getparam(self.SlidingWindow.__name__)
        if self.__windows__ is None:
            self.__confidence_threshold__ = slidingwindowconfig[self.SlidingWindow.ConfidenceThreshold]
            self.__windows__ = self.generatewindows(slidingwindowconfig, x_dim, y_dim, xy_avg)

#         # Try the HAAR cascade classifier:
#         if self.isplotting():
#             cascade = cv2.CascadeClassifier('/Users/safdar/Documents/self-driving-car/advanced-lane-lines/data/cascade/checkcas.xml')
#             objects = cascade.detectMultiScale(latest, scaleFactor=1.1, minNeighbors=2, minSize=(15, 15), flags=cv2.CASCADE_SCALE_IMAGE)
#             img = np.copy(latest)
#             for (x,y,w,h) in objects:
#                 cv2.rectangle(img, (x,y), (x+w,y+h), self.StrongWindowColor, 4)
#             self.__plot__(frame, Image("Cascade Detections", img, None))

        # Perform search:
        image = np.copy(latest)
        weak_candidate_vehicles = []
        strong_candidate_vehicles = []
        for i, scan in enumerate(self.__windows__):
            for j, (x1, x2, y1, y2) in enumerate(scan):
                snapshot = image[y1:y2,x1:x2,:]
                window = snapshot.astype(np.float32)
                window = window/255
#                 window /= np.max(np.abs(snapshot),axis=0)
                features = self.__feature_extractor__.extract(window)
#                 features = np.array(features, dtype=np.float64)
#                 X_scaler = StandardScaler().fit([features])
#                 scaled_features = X_scaler.transform([features])
#                 sample = scaled_features.reshape(1, -1)
                label = self.__classifier__.predict([features])
                score = self.__classifier__.decision_function([features])[0] if "decision_function" in dir(self.__classifier__) else None
                if label == 1 or label == [1]:
                    if score is None or score > self.__confidence_threshold__:
                        strong_candidate_vehicles.append(((x1,x2,y1,y2), score))
                        if self.islogginghits():
                            self.log(self.__hits_folder__, snapshot, i, j)
                    else:
                        weak_candidate_vehicles.append(((x1,x2,y1,y2), score))
                else:
                    if self.isloggingmisses():
                        self.log(self.__misses_folder__, snapshot, i, j)
        self.__frame_vehicles__ = strong_candidate_vehicles
        if self.islogginghits() or self.isloggingmisses():
            imagedumpfile = os.path.join(self.__log_folder__, "{:04d}.png".format(self.__frame_counter__))
            towrite = PIL.Image.fromarray(latest)
            towrite.save(imagedumpfile)
        self.setdata(data, self.FrameVehicleDetections, self.__frame_vehicles__)

        if self.isplotting():
            all_windows = [x for sublist in self.__windows__ for x in sublist]
            # First show all windows being searched:
            image_all = np.zeros_like(latest)
            for scan in self.__windows__:
                for (x1,x2,y1,y2) in scan:
                    cv2.rectangle(image_all, (x1,y1), (x2,y2), self.AllWindowColor, 2)
                    
            # Then show all windows that were weak candidates:            
            image_weak = np.zeros_like(latest)
            for ((x1,x2,y1,y2), score) in weak_candidate_vehicles:
                cv2.rectangle(image_weak, (x1,y1), (x2,y2), self.WeakWindowColor, 2)
                if score is not None:
                    cv2.putText(image_weak,"{:.2f}".format(score), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.WeakWindowColor, 1)

            # Then show all windows that were strong candidates:
            image_strong = np.copy(latest)
            for ((x1,x2,y1,y2), score) in strong_candidate_vehicles:
                cv2.rectangle(image_strong, (x1,y1), (x2,y2), self.StrongWindowColor, 4)
                if score is not None:
                    cv2.putText(image_strong,"{:.2f}".format(score), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.StrongWindowColor, 1)

            # Now superimpose all 3 frames onto the latest color frame:
            todraw = cv2.addWeighted(image_strong, 1, image_all, 0.2, 0)
            todraw = cv2.addWeighted(todraw, 1, image_weak, 0.5, 0)
#             todraw = cv2.addWeighted(todraw, 1, image_strong, 1, 0)
            self.__plot__(frame, Image("Vehicle Search & Hits (All/Weak/Strong = {}/{}/{})".format(
                                        len(all_windows),
                                        len(weak_candidate_vehicles), 
                                        len(strong_candidate_vehicles)),
                                       todraw, None))

            # Try group rectangles:
#             cons = np.copy(latest)
#             if len(self.__frame_vehicles__)>0:
#                 grouped, weights = cv2.groupRectangles(list(zip(*self.__frame_vehicles__))[0], 1, .2)
#                 for ((x1,x2,y1,y2), weight) in zip(grouped, weights):
#                     cv2.rectangle(cons, (x1,y1), (x2,y2), self.StrongWindowColor, 3)
#                     cv2.putText(cons,"{}".format(weight), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, self.StrongWindowColor, 1)
#             self.__plot__(frame, Image("Grouped", cons, None))
            
        self.__frame_counter__+=1
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

