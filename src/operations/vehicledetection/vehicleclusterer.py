'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
from operations.vehicledetection.vehiclefinder import VehicleFinder
import numpy as np
from utils.plotter import Image

import cv2
from operations.vehicledetection.clusterers import PerspectiveDBSCANClustererImpl,\
    ClustererFactory

class VehicleClusterer(Operation):
    # Configuration:
    Clusterer = 'Clusterer'
    
    # Outputs:
    ClusterCandidates = 'ClusterCandidates'
    
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
        mergedcandidates = self.__clusterer__.clusterandmerge(framecandidates)
        self.setdata(data, self.ClusterCandidates, mergedcandidates)

        if self.isplotting():
            clustered = np.copy(latest)
            for candidate in mergedcandidates:
                (x1,x2,y1,y2) = candidate.boundary()
                cv2.rectangle(clustered, (x1,y1), (x2,y2), self.BoxColor, 6)
            self.__plot__(frame, Image("Clustered Candidates", clustered, None))
        return latest
        