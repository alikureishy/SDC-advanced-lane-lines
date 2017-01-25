'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from operations.vehiclefinder import VehicleFinder
from math import sqrt
import numpy as np
from utils.plotter import Image
import cv2
from operations.vehicleclusterer import VehicleClusterer, Detection


# This class creates objects for each box that is detected.
# Each box is then tracked.
# Need a way to merge boxes when they represent the same object.
#    - How to determine that boxes represent the same object?
#    - Weight each object by the number of neighbor boxes
#    -
'''
Compare if car detection corresponds to an earlier detection (mostly if it is close enough).
If yes, update the previous detection with new position using a Kalman filter.
If not, create a new car object.
If I dont detect something for 5 frames i delete it.
'''
class Car(object):
    def __init__(self, lifespan):
        self.__lifespan__ = lifespan
        self.__lookback__ = lifespan
        self.__age__ = 0
        self.__decay__ = 1
        self.__detections__ = np.empty((0,8), dtype=np.int32)
        self.__aggregate_detection__ = None # This can be a Kalman filter
    def confidence(self):
        hits = np.zeros((self.__lifespan__,), dtype=np.bool)
        hits[self.__detections__[:,2]>0] = 1
        s = np.sum(hits)
        return s/self.__lifespan__
    def add_detection(self, detection):
        self.__age__ += 1
        self.__detections__ = np.append(self.__detections__, [detection.nparray()], axis=0)
        if len(self.__detections__) > self.__lookback__:
            self.__detections__ = np.delete(self.__detections__, 0, axis=0)
        if np.sum(self.__detections__[:,2]) > 0:
            average = np.average(self.__detections__, weights=self.__detections__[:,2], axis=0).astype(np.int32)
            self.__aggregate_detection__ = Detection(tuple(average[0:2]), average[2], average[3], tuple(average[4:]))
        else:
            self.__aggregate_detection__ = None
        # Update a Kalman filter here eventually
        
    def projected_gap(self, detection):
        projected = self.project()
        if projected is not None:
            (x1,y1) = projected.center()
            (x2,y2) = detection.center()
            distance = int(sqrt((x1-x2)**2 + (y1-y2)**2))
            gap = distance - (projected.diagonal()/2 + detection.diagonal()/2)
            return gap
        return None
    def project(self, frames=1):
        return self.__aggregate_detection__ # Eventually return a Detection instance that is predicted by a Kalman filter
    def boundary(self):
        if self.__aggregate_detection__ is not None:
            return self.__aggregate_detection__.box()
        return None
    def get_previous_locations(self):
        return self.__detections__[:,0:2]
    def decay(self):
        self.__age__ += 1
        self.__decay__ += 1
        self.add_detection(Detection.empty())
    def dead(self):
        return self.__aggregate_detection__ == None
    def age(self):
        return self.__age__
    def longevity(self):
        return self.__lifespan__ - self.__decay__
    def lifespan(self):
        return self.__lifespan__

class CarTracker(object):
    def __init__(self, drift_tolerance, lookback_frames):
        self.__drift_tolerance__ = drift_tolerance
        self.__lookback_frames__ = lookback_frames
        self.__cars__ = []
    
    def __get_closest_car__(self, detection):
        closest = None
        mindistance = None
        for car in self.__cars__:
            distance = car.projected_gap(detection)
            if (mindistance is None) or (distance is not None and distance < mindistance):
                mindistance = distance
                closest = car
        return closest, mindistance
        
    # Detection: (center, diagonal, score, box)
    def add_detections(self, detections):
        newcars = []
        updatedcars = []
        for detection in detections:
            closest, distance = self.__get_closest_car__(detection)
            if closest is not None and distance < self.__drift_tolerance__:
                closest.add_detection(detection)
                updatedcars.append(closest)
            else:
                car = Car(self.__lookback_frames__)
                car.add_detection(detection)
                newcars.append(car)
        prunedcars = []
        remainingcars = [x for x in self.__cars__ if x not in updatedcars]
        for car in remainingcars:
            car.decay()
            if not car.dead():
                prunedcars.append(car)
        self.__cars__ = prunedcars + updatedcars + newcars
        
    def get_cars(self, confidence_threshold=None, age_threshold=None):
        certaintyfilter = []
        for car in self.__cars__:
            if confidence_threshold is None or car.confidence() >= confidence_threshold:
                certaintyfilter.append(car)
        agefilter = []
        for car in certaintyfilter:
            if age_threshold is None or car.age() >= age_threshold:
                agefilter.append(car)                
        return agefilter # List of "Car" objects

class VehicleTracker(Operation):
    # Configuration:
    DriftToleranceRatio = 'DriftToleranceRatio'
    LookBackFrames = 'LookBackFrames'
    
    # Constants:
    StrongWindowColor = [255, 0, 0]
    
    # Outputs:
    CarTracker = 'CarTracker'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__car_tracker__ = None

    def __processupstream__(self, original, latest, data, frame):
        if self.__car_tracker__ is None:
            drift_tolerance = int(self.getparam(self.DriftToleranceRatio) * np.average(latest.shape[0:2]))
            self.__car_tracker__ = CarTracker(drift_tolerance, self.getparam(self.LookBackFrames))
        
        # Detection: (center, diagonal, score, box)
        detections = self.getdata(data, VehicleClusterer.ClusterVehicles, VehicleClusterer)
        self.__car_tracker__.add_detections(detections)
        self.setdata(data, self.CarTracker, self.__car_tracker__)

        if self.isplotting():
            allcars = np.copy(latest)
            tracked_cars = self.__car_tracker__.get_cars()
            for car in tracked_cars:
                assert len(car.boundary())==4, "Car boundary box not well defined. Tracked car length: {}".format(len(tracked_cars))
                (x1,x2,y1,y2) = car.boundary()
                cv2.rectangle(allcars, (x1,y1), (x2,y2), self.StrongWindowColor, 2)
                age = car.age()
                countdown = car.longevity()
                cv2.putText(allcars,"{}/{}".format(age, countdown), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.StrongWindowColor, 1)
#                 history = car.get_previous_locations().astype(np.int32)
#                 if len(history) > 0:
#                     cv2.polylines(allcars, [history], False, self.StrongWindowColor, thickness=2, lineType=cv2.LINE_4)
#                     for point in history:
#                         cv2.circle(allcars, tuple(point), 4, self.StrongWindowColor, -1)
            self.__plot__(frame, Image("All Tracked Cars", allcars, None))
            
        return latest
        