'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from operations.vehiclefinder import Candidate, VehicleFinder, Box
from math import sqrt
import numpy as np
from utils.plotter import Image
import cv2
from operations.vehicleclusterer import VehicleClusterer


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

class Vehicle(Candidate):
    def __init__(self, center, score, diagonal, lookback=5):
        Candidate.__init__(self, center, score, diagonal)
        self.__lookback__ = lookback
        self.__history__ = np.empty((0, 4), dtype=np.int32)
        self.__continuous_hits__ = 0
        self.__continuous_misses__ = 0
        self.__hits__ = 0
        self.__misses__ = 0
        self.__merged__ = False
    def hit(self, detection):
        self.__hits__ += 1
        self.__continuous_hits__ += 1
        self.__continuous_misses__ = 0
        self.addlocation(detection)
    def miss(self):
        self.__misses__ += 1
        self.__continuous_hits__ = 0
        self.__continuous_misses__ += 1
#         self.addlocation(detection=None)
#     def addlocation(self, detection=None):
#         if detection is None:
#             if len(self.__history__) > 0:
#                 self.__history__ = np.append(self.__history__, [self.__history__[-1]], axis=0)
#         else:
#             self.__history__ = np.append(self.__history__, [detection.nparray()], axis=0)
#         if len(self.__history__) > self.__lookback__:
#             self.__history__ = np.delete(self.__history__, 0, axis=0)
#         self.__center__ = np.average(self.__history__[:,0], weights=self.__history__[:,2], axis=0).astype(np.int32)
#         self.__diagonal__ = np.average(self.__history__[:,1], weights=self.__history__[:,2], axis=0).astype(np.int32)
#         self.__score__ = np.average(self.__history__[:,2], axis=0).astype(np.int32) # Only simple average for score
    def projected_gap(self, detection, frames=1):
        projected = self.project(frames=frames)
        if projected is not None:
            (x1,y1) = projected.center()
            (x2,y2) = detection.center()
            distance = int(sqrt((x1-x2)**2 + (y1-y2)**2))
            gap = distance - (projected.diagonal()/2 + detection.diagonal()/2)
            return gap
        return None
    def project(self, frames=1):
        return self # Eventually return a Candidate instance that is predicted by a Kalman filter
    def continuous_hits(self):
        return self.__continuous_hits__
    def continuous_misses(self):
        return self.__continuous_misses__
    def hits(self):
        return self.__hits__
    def misses(self):
        return self.__misses__
    def location_history(self):
        return self.__history__[:,0:2]
    def isdefunct(self):
        return self.__misses__ > self.__hits__
    def makedefunct(self):
        self.__misses__ = 1
        self.__hits__ = -1
    def wasmerged(self):
        return self.__merged__
    def age(self):
        return self.__hits__ + self.__misses__
    def satisfies(self, continuity_threshold=None):
        return not self.isdefunct() and (continuity_threshold is None or self.continuous_hits() >= continuity_threshold)
    def nparray(self):
        return np.array([*Candidate.nparray(self), self.hits(), self.continuous_hits(), self.misses(), self.continuous_misses()])
    @staticmethod
    def merge(vehicles):
        if len(vehicles) == 0:
            return None
        elif len(vehicles) == 1:
            if vehicles[0].age() > 0:
                vehicles[0].miss() # Register a miss because this vehicle hasn't been merged with a new location
            return vehicles[0]
        else:
            asarray = np.array([x.nparray() for x in vehicles])
            center = np.average(asarray[:,0:2], weights=asarray[:,2], axis=0).astype(np.int32)
            # Consider 3*Sigma again, or perhaps stick with average?
            diagonal = np.average(asarray[:,2], weights=asarray[:,2], axis=0).astype(np.int32)
            score = np.average(asarray[:,3], axis=0).astype(np.int32) # Only simple average for score
            hits = np.max(asarray[:,4]).astype(np.int32)
            conthits = np.max(asarray[:,5]).astype(np.int32)
            misses = np.max(asarray[:,6]).astype(np.int32)
            map(lambda x: x.makedefunct(), vehicles)
            mergedvehicle = Vehicle(center, diagonal, score)
            mergedvehicle.__hits__ = hits + 1
            mergedvehicle.__continuous_hits__ = conthits + 1
            mergedvehicle.__misses__ = misses
            mergedvehicle.__continuous_misses__ = 0
            mergedvehicle.__merged__ = True
            return mergedvehicle

class VehicleManager(object):
    def __init__(self, drift_tolerance, lookback_frames):
        self.__drift_tolerance__ = drift_tolerance
        self.__lookback_frames__ = lookback_frames
        self.__vehicles__ = []

    @staticmethod
    def get_distance_matrix(vehicles, imageshape, windowsizerange):
        distances = np.full((len(vehicles), len(vehicles)), fill_value=0, dtype=np.int32)
        for i, leftbox in enumerate(vehicles):
            for j, rightbox in enumerate(vehicles):
                if i == j:
                    continue
#                 distances[i][j] = distances[j][i] = Box.get_perspective_distance(leftbox, rightbox, imageshape, windowsizerange)
                distances[i][j] = distances[j][i] = Box.get_manhattan_distance(leftbox, rightbox)
        return distances
    
    # Candidate: (center, diagonal, score)
    def add_candidates(self, candidates, windowrange, xydims):
        existing_vehicles = self.get_vehicles()
        vehicles_to_add = [Vehicle(candidate.center(), candidate.diagonal(), candidate.score()) for candidate in candidates]
        combined_list = vehicles_to_add + existing_vehicles
        
        print ("Existing tracked vehicles: {}".format(len(existing_vehicles)))
        print ("New tracking candidates: {}".format(len(vehicles_to_add)))
        # Cluster across space AND time:
        mergedvehicles = []
        if len(combined_list) > 0:
            centers = np.array([x.center() for x in combined_list])
            scores = np.array([x.score() for x in combined_list])
            distancemaxtrix = VehicleManager.get_distance_matrix(combined_list, xydims, windowrange)
            minsamples = 1
            dbscan = DBSCAN(eps=self.__drift_tolerance__, min_samples=minsamples)
            dbscan_distance_matrix = DBSCAN(eps=self.__drift_tolerance__, metric='precomputed', min_samples=minsamples)
            clusterer = dbscan.fit(centers, sample_weight=scores)
            clusterer_distance_matrix = dbscan_distance_matrix.fit(distancemaxtrix, sample_weight=scores)
            labels = clusterer.labels_
            labels_distance_matrix = clusterer_distance_matrix.labels_

            # Collect the boundary numbers in each cluster:
            clusters = {}
            for i,label in enumerate(labels_distance_matrix):
                if label==-1:
                    continue
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(combined_list[i])

            # Generate a clustered Candidate for each cluster:
            for cluster in clusters:
                mergedvehicles.append(Vehicle.merge(clusters[cluster]))
        print ("Post-merge tracked vehicles: {}".format(len(mergedvehicles)))
        self.__vehicles__ = mergedvehicles
        
    def get_vehicles(self, continuity_threshold=None):
        filtered = []
        for vehicle in self.__vehicles__:
            if vehicle.satisfies(continuity_threshold):
                filtered.append(vehicle)
        return filtered

class VehicleTracker(Operation):
    # Configuration:
    DriftToleranceRatio = 'DriftToleranceRatio'
    LookBackFrames = 'LookBackFrames'
    
    # Constants:
    VehicleWindowColor = [255, 0, 0]
    MergedVehicleColor = [155, 0, 0]
    
    # Outputs:
    VehicleManager = 'VehicleManager'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__vehicle_manager__ = None
        self.__drift_tolerance__ = None

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim = latest.shape[1], latest.shape[0]
        if self.__vehicle_manager__ is None:
            self.__drift_tolerance__ = int(self.getparam(self.DriftToleranceRatio) * np.average(latest.shape[0:2]))
            self.__vehicle_manager__ = VehicleManager(self.__drift_tolerance__, self.getparam(self.LookBackFrames))
        
        # Candidate: (center, diagonal, score)
        detections = self.getdata(data, VehicleClusterer.ClusterCandidates, VehicleClusterer)
        windowrange = self.getdata(data, VehicleFinder.WindowSizeRange, VehicleFinder)
        self.__vehicle_manager__.add_candidates(detections, windowrange, (x_dim,y_dim))

        if self.isplotting():
            allvehicles = np.copy(latest)
            tracked_vehicles = self.__vehicle_manager__.get_vehicles()
            print ("Plotting {} vehicles".format(len(tracked_vehicles)))
            for vehicle in tracked_vehicles:
                (x1,x2,y1,y2) = vehicle.boundary()
                if vehicle.wasmerged():
                    cv2.rectangle(allvehicles, (x1,y1), (x2,y2), self.MergedVehicleColor, 3)
                else:
                    cv2.rectangle(allvehicles, (x1,y1), (x2,y2), self.VehicleWindowColor, 2)
                cv2.putText(allvehicles,\
                            "[{} - {}, {}/{}, {}/{}]".format(\
                                                        "Merged" if vehicle.wasmerged() else "New",\
                                                        vehicle.age(), \
                                                        vehicle.continuous_hits(),\
                                                        vehicle.hits(),\
                                                        vehicle.continuous_misses(),\
                                                        vehicle.misses()),\
                            (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.VehicleWindowColor, thickness=2)
#                 history = vehicle.location_history().astype(np.int32)
#                 if len(history) > 0:
#                     cv2.polylines(allvehicles, [history], False, self.StrongWindowColor, thickness=2, lineType=cv2.LINE_4)
#                     for point in history:
#                         cv2.circle(allvehicles, tuple(point), 4, self.StrongWindowColor, -1)
            self.__plot__(frame, Image("Tracked Cars", allvehicles, None))

        self.setdata(data, self.VehicleManager, self.__vehicle_manager__)
        return latest
        