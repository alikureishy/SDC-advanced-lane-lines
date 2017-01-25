'''
Created on Jan 15, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from operations.vehicletracker import VehicleTracker
import cv2

class VehicleMarker(Operation):
    # Configuration:
    CertaintyThreshold = 'CertainThreshold'
    AgeThreshold = 'AgeThreshold'
    
#     CurrentBoundingBoxColor = 'CurrentBoundingBoxColor'
    
    # Constants:
    StrongWindowColor = [255, 0, 0]
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__certainty_threshold__ = params[self.CertaintyThreshold]
        self.__age_threshold__ = params[self.AgeThreshold]
#         self.__bounding_box_color__ = params[self.CurrentBoundingBoxColor]

    def __processdownstream__(self, original, latest, data, frame):
        cartracker = self.getdata(data, VehicleTracker.CarTracker, VehicleTracker)
        cars = cartracker.get_cars(certainty_threshold=self.__certainty_threshold__, age_threshold=self.__age_threshold__)
        for car in cars:
            (x1,x2,y1,y2) = car.get_box()
            cv2.rectangle(latest, (x1,y1), (x2,y2), self.StrongWindowColor, 2)
        return latest
