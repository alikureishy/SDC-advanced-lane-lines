'''
Created on Jan 14, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from sklearn.externals import joblib
from statistics import mean
import numpy as np
import cv2
from extractors.helper import buildextractor
import os
from utils.plotter import Image
import PIL
import time
from sklearn.preprocessing.data import StandardScaler
import math
from builtins import staticmethod

class Box(object):
    def __init__(self, center, diagonal, bounds=None):
        assert  (center is not None and diagonal is not None), "Invalid input"
        self.__center__ = center
        self.__diagonal__ = diagonal
        (cx, cy) = self.__center__
        s = int(math.sqrt(((self.__diagonal__ ** 2) / 2)))
        leftx, rightx, topy, bottomy = cx - (s // 2), cx + (s // 2), cy - (s // 2), cy + (s // 2)
        if bounds is not None:
            xrange, yrange=bounds[0], bounds[1]
            if leftx < xrange[0]:
                leftx = xrange[0]
            if rightx > xrange[1]:
                rightx = xrange[1]
            if topy < yrange[0]:
                topy = yrange[0]
            if bottomy > yrange[1]:
                bottomy = yrange[1]
            self.__fitted__ = True
        else:
            self.__fitted__ = False
        assert not (leftx == rightx) or not (topy == bottomy), "Zero sized window found with center: {}, size: {}".format(center, diagonal)
        self.__boundary__ = (leftx, rightx, topy, bottomy)
    def fitted(self):
        return self.__fitted__
    def center(self):
        return self.__center__
    def score(self):
        return self.__score__
    def diagonal(self):
        return self.__diagonal__
    def boundary(self):
        return self.__boundary__
    # This method determines distance between two boxes as being
    # inversely proportional to the box size. The distance between
    # large boxes is the same as the distance in actual pixels.
    # Distance between smaller boxes is inversely proportional
    # to the difference in the size. A small box is far in the horizon. Larger boxes are closer.
    @staticmethod
    def get_perspective_distance(leftbox, rightbox, imageshape, windowrange):
        maxwindow = max(windowrange)
        # Y-magnification depends on size ratio of the two boxes
        ymagnification = min(rightbox.diagonal()/leftbox.diagonal(), leftbox.diagonal()/rightbox.diagonal())
        # X-magnification depends on the size ratio of small box relative to the biggest box
        xmagnification = maxwindow / min(leftbox.diagonal(), rightbox.diagonal())
        dx = np.absolute(leftbox.center()[0] - rightbox.center()[0]) * xmagnification
        dy = np.absolute(imageshape[1] * ymagnification) # np.absolute(leftcenter[1] - rightcenter[1]) * ymagnification
        distance = int(math.sqrt(dx**2 + dy**2))
#         print ("Perspective: {} <--> {} : ({}, {})".format(leftbox.diagonal(), rightbox.diagonal(), dx, dy))
        return distance
    @staticmethod
    def get_manhattan_distance(leftbox, rightbox):
        dx = np.absolute(leftbox.center()[0] - rightbox.center()[0])
        dy = np.absolute(leftbox.center()[1] - rightbox.center()[1])
        distance = int(math.sqrt(dx**2 + dy**2))
        return distance
    @staticmethod
    def get_distance_matrix(candidates, imageshape, windowsizerange):
        distances = np.full((len(candidates), len(candidates)), fill_value=0, dtype=np.int32)
        for i, leftbox in enumerate(candidates):
            for j, rightbox in enumerate(candidates):
                if i == j:
                    continue
                distances[i][j] = distances[j][i] = Box.get_perspective_distance(leftbox, rightbox, imageshape, windowsizerange)
        return distances
    @staticmethod
    def cluster(boxes):
        return [[]] # Returns a list (rows) of lists (columns). Each row represents one cluster of boxes. 

class Candidate(Box):
    def __init__(self, center, diagonal, score):
        assert  (center is not None and score is not None and diagonal is not None), "Invalid input"
        Box.__init__(self, center, diagonal)
        self.__score__ = score
    def score(self):
        return self.__score__
    def nparray(self):
        return np.array([*self.center(), self.diagonal(), self.score()], dtype=np.int32)
    @staticmethod
    def merge(candidates):
        if len(candidates) == 0:
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            asarray = np.array([x.nparray() for x in candidates])
            # Center is the centroid of the candidates' centers:
            center = np.average(asarray[:,0:2], weights=asarray[:,2], axis=0).astype(np.int32)
            # Instead of being the average, perhaps consider different options. Like
            # the 3*Sigma of the candidates' diagonals?
            diagonal = np.average(asarray[:,2], weights=asarray[:,2], axis=0).astype(np.int32)
            # Score could perhaps also be the 3*Sigma.
            score = np.average(asarray[:,3], axis=0).astype(np.int32) # Only simple average for score
            mergedcandidate = Candidate(center, diagonal, score)
            mergedcandidate.__merged__ = True
            return mergedcandidate

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
    FrameCandidates = "FrameCandidates"
    WindowSizeRange = 'WindowSizeRange'

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
        
        self.__frame_candidates__ = None
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
            self.__continuity_threshold__ = slidingwindowconfig[self.SlidingWindow.ConfidenceThreshold]
            self.__windows__ = self.generatewindows(slidingwindowconfig, x_dim, y_dim, xy_avg)
            self.__window_range_ratio__ = slidingwindowconfig[self.SlidingWindow.WindowRangeRatio]
            self.__window_range__ = [int(xy_avg * r) for r in self.__window_range_ratio__]
        self.setdata(data, self.WindowSizeRange, self.__window_range__)

        # Perform search:
        image = np.copy(latest)
        weak_candidates = []
        strong_candidates = []
        for i, scan in enumerate(self.__windows__):
            for j, box in enumerate(scan):
                (x1, x2, y1, y2) = box.boundary()
                snapshot = image[y1:y2,x1:x2,:]
                if np.min(snapshot) == 0 and np.max(snapshot)==0:
                    continue
                window = snapshot.astype(np.float32)
                if np.max(window) == 0:
                    print ("Error")
                window = window/255
#                 window /= np.max(np.abs(snapshot),axis=0) #TODO: Check axis setting. Might have to be 1
                features = self.__feature_extractor__.extract(window)
#                 features = np.array(features, dtype=np.float64)
#                 X_scaler = StandardScaler().fit([features])
#                 scaled_features = X_scaler.transform([features])
#                 sample = scaled_features.reshape(1, -1)
                try:
                    label = self.__classifier__.predict([features])
                except ValueError:
                    print ("Error")
                    
                score = self.__classifier__.decision_function([features])[0] if "decision_function" in dir(self.__classifier__) else None
                if label == 1 or label == [1]:
                    if score is None or score > self.__continuity_threshold__:
                        strong_candidates.append(Candidate(box.center(), box.diagonal(), score))
                        if self.islogginghits():
                            self.log(self.__hits_folder__, snapshot, i, j)
                    else:
                        weak_candidates.append(Candidate(box.center(), box.diagonal(), score))
                else:
                    if self.isloggingmisses():
                        self.log(self.__misses_folder__, snapshot, i, j)
        self.__frame_candidates__ = strong_candidates
        self.setdata(data, self.FrameCandidates, self.__frame_candidates__)
        
        if self.islogginghits() or self.isloggingmisses():
            imagedumpfile = os.path.join(self.__log_folder__, "{:04d}.png".format(self.__frame_counter__))
            towrite = PIL.Image.fromarray(latest)
            towrite.save(imagedumpfile)

        if self.isplotting():
            all_windows = [x for sublist in self.__windows__ for x in sublist]
            # First show all windows being searched:
            image_all = np.zeros_like(latest)
            for scan in self.__windows__:
                for box in scan:
                    (x1,x2,y1,y2) = box.boundary()
                    cv2.rectangle(image_all, (x1,y1), (x2,y2), self.AllWindowColor, 2)
                    if box.fitted():
                        cv2.putText(image_all,"~x~x~", (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.WeakWindowColor, 1)
                    
            # Then show all windows that were weak candidates:            
            image_weak = np.zeros_like(latest)
            for candidate in weak_candidates:
                (x1,x2,y1,y2) = candidate.boundary()
                cv2.rectangle(image_weak, (x1,y1), (x2,y2), self.WeakWindowColor, 2)
                if candidate.score() is not None:
                    cv2.putText(image_weak,"{:.2f}".format(candidate.score()), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.WeakWindowColor, 1)

            # Then show all windows that were strong candidates:
            image_strong = np.copy(latest)
            for candidate in strong_candidates:
                (x1,x2,y1,y2) = candidate.boundary()
                cv2.rectangle(image_strong, (x1,y1), (x2,y2), self.StrongWindowColor, 4)
                if candidate.score() is not None:
                    cv2.putText(image_strong,"{:.2f}".format(candidate.score()), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.StrongWindowColor, 1)

            # Now superimpose all 3 frames onto the latest color frame:
            todraw = cv2.addWeighted(image_strong, 1, image_all, 0.2, 0)
            todraw = cv2.addWeighted(todraw, 1, image_weak, 0.5, 0)
#             todraw = cv2.addWeighted(todraw, 1, image_strong, 1, 0)
            self.__plot__(frame, Image("Vehicle Search & Hits (All/Weak/Strong = {}/{}/{})".format(
                                        len(all_windows),
                                        len(weak_candidates), 
                                        len(strong_candidates)),
                                       todraw, None))

            # Try group rectangles:
#             cons = np.copy(latest)
#             if len(self.__frame_candidates__)>0:
#                 grouped, weights = cv2.groupRectangles(list(zip(*self.__frame_candidates__))[0], 1, .2)
#                 for ((x1,x2,y1,y2), weight) in zip(grouped, weights):
#                     cv2.rectangle(cons, (x1,y1), (x2,y2), self.StrongWindowColor, 3)
#                     cv2.putText(cons,"{}".format(weight), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, self.StrongWindowColor, 1)
#             self.__plot__(frame, Image("Grouped", cons, None))
            
        self.__frame_counter__+=1
        return latest

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
            center_box = Box(center, boxwidth)
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
                    if not leftcenter[0] in range(0,x_dim) or not leftcenter[1] in range(0,y_dim):
                        continue
                    left_box = Box(leftcenter, boxwidth, bounds=((0,x_dim),(0,y_dim)))
                    rightcenter = (center[0] + (j * boxwidth) + (k * boxshift), center[1])
                    if not rightcenter[0] in range(0,x_dim) or not rightcenter[1] in range(0,y_dim):
                        continue
                    right_box = Box(rightcenter, boxwidth)
                    windows[i].append(left_box)
                    windows[i].append(right_box)
                    print ("\t\t\t\tShift # {}: <--{} {} {}-->".format(k, left_box, '~'*(k+1), right_box))
            print ("\tTotal boxes in scan: {}".format(len(windows[i])))
        return windows

