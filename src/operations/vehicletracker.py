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

import math
import cv2
from operations.vehicleclusterer import VehicleClusterer


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
    def __init__(self):
        pass
    def get_box(self):
        return (500,600,350,450)
    def get_tracking_age(self):
        4
    def get_previous_locations(self):
        return np.array([(550,500), (565,575), (580,625), (600,650), (620,675)])

class CarTracker(object):
    def __init__(self, drift_tolerance, lookback_frames):
        self.__drift_tolerance__ = drift_tolerance
        self.__lookback_frames__ = lookback_frames
    def add_measurement(self, vehicles, boxes):
        pass
    def get_cars(self, certainty_threshold=None, age_threshold=None):
        return [Car()] # List of "Car" objects

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
        
        # Vehicle: (center, diagonal, score)
        vehicles = self.getdata(data, VehicleClusterer.ClusterVehicles, VehicleClusterer)
        boxes = self.getdata(data, VehicleClusterer.ClusterBoxes, VehicleClusterer)
        
        self.__car_tracker__.add_measurement(vehicles, boxes)
        self.setdata(data, self.CarTracker, self.__car_tracker__)

        if self.isplotting():
            allcars = np.copy(latest)
            tracked_cars = self.__car_tracker__.get_cars()
            for car in tracked_cars:
                (x1,x2,y1,y2) = car.get_box()
                cv2.rectangle(allcars, (x1,y1), (x2,y2), self.StrongWindowColor, 2)
                age = car.get_tracking_age()
                cv2.putText(allcars,"{}".format(age), (x1,y1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.StrongWindowColor, 1)
                history = car.get_previous_locations()
                if len(history) > 0:
                    cv2.polylines(allcars, [history], False, self.StrongWindowColor, thickness=2, lineType=cv2.LINE_4)
                    for point in history:
                        cv2.circle(allcars, tuple(point), 4, self.StrongWindowColor, -1)
            self.__plot__(frame, Image("All Tracked Cars", allcars, None))
            
        return latest
        