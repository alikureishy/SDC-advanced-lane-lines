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

class VehicleFinder(Operation):
    ClassifierFile = 'ClassifierFile'
    FeatureExtractors = 'FeatureExtractors'
    class Plottable(object):
        ToPlot = 'ToPlot'
    class SlidingWindow(Plottable):
        DepthRangeRatio = 'DepthRangeRatio'
        DefaultHeadingRatios = 'DefaultHeadingRatios'
        CenterShiftRatio = 'CenterShiftRatio'
        SizeVariations = 'SizeVariations'
        WindowRangeRatio = 'WindowRangeRatio'
        StepRatio = 'StepRatio'
    class SpatialBinning(Plottable):
        Space = 'Space'
        Size = 'Size'
    class ColorHistogram(Plottable):
        Space = 'Space'
        NumBins = 'NumBins'
        BinRange = 'BinRange'
    class HOGExtractor(Plottable):
        Orientations = 'Orientations'
        HogChannel = 'HogChannel'
        PixelsPerCell = 'PixelsPerCell'
        CellsPerBlock = 'CellsPerBlock'
        Size = 'Size'

    # Constants:
    HitWindowColor = [152, 251, 152]
    MissWindowColor = [255,160,122]

    def __init__(self, params):
        Operation.__init__(self, params)

        # Classifier
        self.__classifier__ = joblib.load(params[self.ClassifierFile])

        # Sliding Window:
        self.__windows__ = None
        
        # Feature Extractors
        extractorsequence = params[self.FeatureExtractors]
        extractors = []
        for config in extractorsequence:
            assert len(config.keys())==1, "Invalid: {}".format(config)
            extractor = None
            if self.ColorHistogram.__name__ in config:
                cfg = config[self.ColorHistogram.__name__]
                extractor = ColorHistogram(color_space=cfg[self.ColorHistogram.Space], 
                                           nbins=cfg[self.ColorHistogram.NumBins], 
                                           bins_range=cfg[self.ColorHistogram.BinRange])
            elif self.SpatialBinning.__name__ in config:
                cfg = config[self.SpatialBinning.__name__]
                extractor = SpatialBinner(color_space=cfg[self.SpatialBinning.Space],
                                          size=cfg[self.SpatialBinning.Size])
            elif self.HOGExtractor.__name__ in config:
                cfg = config[self.HOGExtractor.__name__]
                extractor = HogExtractor(orientations=cfg[self.HOGExtractor.Orientations],
                                          hog_channel=cfg[self.HOGExtractor.HogChannel],
                                          size=cfg[self.SpatialBinning.Size],
                                          pixels_per_cell=cfg[self.HOGExtractor.PixelsPerCell],
                                          cells_per_block=cfg[self.HOGExtractor.CellsPerBlock])
            else:
                raise ("Unrecognized extractor provided")
            extractors.append(extractor)
        self.__feature_extractor__ = FeatureCombiner(tuple(extractors))

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim, xy_avg = latest.shape[1], latest.shape[0], int(mean(latest.shape[0:2]))
        slidingwindowconfig = self.getparam(self.SlidingWindow.__name__)
        if self.__windows__ is None:
            self.__windows__ = self.generatewindows(slidingwindowconfig, x_dim, y_dim, xy_avg)

        # Illustrate boxes:
        if self.isplotting():
            image = np.copy(latest)
            for scan in self.__windows__:
                for (x1,x2,y1,y2) in scan:
                    cv2.rectangle(image, (x1,y1), (x2,y2), self.MissWindowColor, 5)
            self.__plot__(frame, image, None, "Vehicle Search Windows", None)
        
        # Perform search:
        image = np.copy(latest)
        detected_vehicles = []
        for scan in self.__windows__:
            for (x1, x2, y1, y2) in scan:
                window = image[y1:y2,x1:x2,:]
                features = self.__feature_extractor__.extract(window)
                label = self.__classifier__.predict(features.reshape(1, -1))
                if label == 1:
                    detected_vehicles.append((x1,x2,y1,y2))

        if self.isplotting():
            image = np.copy(latest)
            for (x1,x2,y1,y2) in detected_vehicles:
                cv2.rectangle(image, (x1,y1), (x2,y2), self.HitWindowColor, 5)
            self.__plot__(frame, image, None, "Vehicle Search Hits", None)
            
        return latest

    def getboxcorners(self, center, size, xrange, yrange):
        s = int(size/2)
        x = center[0]
        y = center[1]
        
        leftx = x-s
        rightx = x+s
        topy = y-s
        bottomy = y+s
        if leftx < xrange[0] or rightx > xrange[1] or topy < yrange[0] or bottomy > yrange[1]:
            return None
        
#         topleft = (leftx, topy)
#         topright = (rightx, topy)
#         bottomleft = (leftx, bottomy)
#         bottomright = (rightx, bottomy)
#         return (topleft, topright, bottomleft, bottomright)
    
        return (leftx, rightx, topy, bottomy) 
    def generatewindows(self, cfg, x_dim, y_dim, xy_avg):
        shift = cfg[self.SlidingWindow.CenterShiftRatio] * x_dim
        # Depth range:
        depth_range_ratio = sorted(cfg[self.SlidingWindow.DepthRangeRatio], reverse=True)
        depth_range = [int(y_dim * r) for r in depth_range_ratio]
        horizon = min(depth_range)
        # Calculate perspective widths for depth range:
        default_heading = cfg[self.SlidingWindow.DefaultHeadingRatios]
        points = getperspectivepoints(x_dim, y_dim, depth_range_ratio, default_heading)
        perspective_widths = sorted([(points[1][0] - points[0][0]), (points[3][0] - points[2][0])])
        # Magnification of scan widths and windows across depth:
        magnification = perspective_widths[1] / perspective_widths[0]
        # Calculate horizon scan range and window size:
        scan_to_perspective_ratio = x_dim / perspective_widths[1]
        horizon_scan_width = int((scan_to_perspective_ratio * perspective_widths[0]) / 2)
        window_range_ratio = cfg[self.SlidingWindow.WindowRangeRatio]
        window_range = [int(xy_avg * r) for r in window_range_ratio]
        size_variations = cfg[self.SlidingWindow.SizeVariations]
        grow_rate = int(np.absolute(window_range[1]-window_range[0])/(size_variations))
        slide_ratio = cfg[self.SlidingWindow.StepRatio]
        # Calculate all the windows:
        center = (int((x_dim / 2) + shift), horizon)
        windows = []
        # Each slice:
        for i in range(size_variations):
            windows.append([])
            scanwidth = horizon_scan_width + (i * grow_rate * magnification)
            boxwidth = window_range[0] + (i * grow_rate)
            center_box = self.getboxcorners(center, boxwidth, [0, x_dim], [0, y_dim])
            if center_box is None:
                continue
            windows[i].append(center_box)
            shifts_per_box = int(1 / slide_ratio)
            boxshift = int(boxwidth * slide_ratio)
            numboxes = int(scanwidth / boxwidth) # Boxes each side of the center box
            # Each box on left + right sides of center:
            for j in range(1, numboxes + 1):
                for k in range(0, shifts_per_box):
                    leftcenter = (center[0] - (j * boxwidth) - (k * boxshift), center[1])
                    left_box = self.getboxcorners(leftcenter, boxwidth, [0, x_dim], [0, y_dim])
                    rightcenter = (center[0] + (j * boxwidth) + (k * boxshift), center[1])
                    right_box = self.getboxcorners(rightcenter, boxwidth, [0, x_dim], [0, y_dim])
                    if left_box is None or right_box is None:
                        continue
                    windows[i].append(left_box)
                    windows[i].append(right_box)
        
        return windows

