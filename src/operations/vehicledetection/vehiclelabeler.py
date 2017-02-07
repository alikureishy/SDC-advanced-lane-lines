'''
Created on Jan 14, 2017

@author: safdar
'''

import numpy as np
import cv2
from operations.baseoperation import Operation
from operations.vehicledetection.vehiclefinder import VehicleFinder
from utils.plotter import Image
from operations.vehicledetection.clusterers import ClustererFactory

class VehicleLabeler(Operation):
    Clusterer = 'Clusterer'

    # Constants:
    BoxColor = [0,0,255]

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__clusterer__ = None

    def __processupstream__(self, original, latest, data, frame):
        if self.__clusterer__ is None:
            config = self.getparam(self.Clusterer)
            config[list(config.keys())[0]]['image_shape'] = latest.shape[0:2]
            self.__clusterer__ = ClustererFactory.create(config)
            
        framecandidates = self.getdata(data, VehicleFinder.FrameCandidates, VehicleFinder)
        clustered = self.__clusterer__.clusterandmerge(framecandidates)
        
        if self.isplotting():
            labeled = np.copy(latest)
            for candidate in clustered:
                (x1,x2,y1,y2) = candidate.boundary()
                cv2.rectangle(labeled, (x1,y1), (x2,y2), self.BoxColor, 6)
            self.__plot__(frame, Image("Labeled Cars", labeled, None))
        
        return latest
