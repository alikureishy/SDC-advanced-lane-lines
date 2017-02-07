'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
from utils.plotter import Image
import cv2
from operations.vehicledetection.vehicleclusterer import VehicleClusterer
from operations.vehicledetection.clusterers import ClustererFactory
from _collections import deque


# This class creates objects for each boundary that is detected.
# Each boundary is then tracked.
# Need a way to merge boxes when they represent the same object.
#    - How to determine that boxes represent the same object?
#    - Weight each object by the number of neighbor boxes
#    -
'''
Compare if vehicle detection corresponds to an earlier detection (mostly if it is close enough).
If yes, update the previous detection with new position using a Kalman filter.
If not, create a new vehicle object.
If I dont detect something for 5 frames i delete it.
'''

class VehicleTracker(Operation):
    # Configuration:
    LookBackFrames = 'LookBackFrames'
    Clusterer = 'Clusterer'
    
    # Constants:
    HistoryVehicleColor = [155, 0, 0]
    TrackedWindowColor = [255, 0, 0]
    
    # Outputs:
    TrackedVehicles = 'TrackedVehicles'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__clusterer__ = None
        self.__lookback_frames__ = params[self.LookBackFrames]
        self.__history__ = deque(maxlen=self.__lookback_frames__)
        self.__vehicles__ = []

    def __get_flattened_history__(self):
        flattened = []
        for detections in self.__history__:
            if detections is not None and len(detections) > 0:
                for detection in detections:
                    flattened.append(detection)
        return flattened

    def __is_history_warmed(self):
        return len(self.__history__) == self.__lookback_frames__
    
    def __add_candidates__(self, candidates):
        self.__history__.append(candidates)
    
    def __processupstream__(self, original, latest, data, frame):
        if self.__clusterer__ is None:
            config = self.getparam(self.Clusterer)
            config[list(config.keys())[0]]['image_shape'] = latest.shape[0:2]
            self.__clusterer__ = ClustererFactory.create(config)
        
        # Candidate: (center, diagonal, score)
        newcandidates = self.getdata(data, VehicleClusterer.ClusterCandidates, VehicleClusterer)
        if self.__is_history_warmed():
            # Once history is warmed, any absent candidates still count towards the history
            self.__add_candidates__(newcandidates)
        elif newcandidates is not None and len(newcandidates) > 0:
            self.__add_candidates__(newcandidates)
            
        flattened = self.__get_flattened_history__()
        if flattened is not None and len(flattened) > 0:
            self.__vehicles__ = self.__clusterer__.clusterandmerge(flattened)
        self.setdata(data, self.TrackedVehicles, self.__vehicles__)

        if self.isplotting():
            historicalview = np.copy(latest)
            allvehicles = self.__get_flattened_history__()
            for vehicle in allvehicles:
                (x1,x2,y1,y2) = vehicle.boundary()
                cv2.rectangle(historicalview, (x1,y1), (x2,y2), self.HistoryVehicleColor, 6)
            self.__plot__(frame, 
                          Image("History - {}".format("Warming..." if not self.__is_history_warmed() else "Warmed"), 
                                historicalview, 
                                None))
            
            mergedview = np.copy(latest)
            tracked_vehicles = self.__vehicles__
            for vehicle in tracked_vehicles:
                (x1,x2,y1,y2) = vehicle.boundary()
                cv2.rectangle(mergedview, (x1,y1), (x2,y2), self.TrackedWindowColor, 6)
            self.__plot__(frame, Image("Tracked Cars", mergedview, None))

        return latest
        