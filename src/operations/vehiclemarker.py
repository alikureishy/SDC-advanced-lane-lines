'''
Created on Jan 15, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from operations.vehicletracker import VehicleTracker
from utils.plotter import Image
import cv2

class VehicleMarker(Operation):
    # Configuration:
    ConfidenceThreshold = 'ConfidenceThreshold'
    AgeThreshold = 'AgeThreshold'
    
#     CurrentBoundingBoxColor = 'CurrentBoundingBoxColor'
    
    # Constants:
    StrongWindowColor = [255, 0, 0]
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__confidence_threshold__ = params[self.ConfidenceThreshold]
        self.__age_threshold__ = params[self.AgeThreshold]
#         self.__bounding_box_color__ = params[self.CurrentBoundingBoxColor]

    def __processdownstream__(self, original, latest, data, frame):
        cartracker = self.getdata(data, VehicleTracker.CarTracker, VehicleTracker)
        cars = cartracker.get_cars(confidence_threshold=self.__confidence_threshold__, age_threshold=self.__age_threshold__)
        for car in cars:
            (x1,x2,y1,y2) = car.boundary()
            cv2.rectangle(latest, (x1,y1), (x2,y2), self.StrongWindowColor, 2)
            
        if self.isplotting():
            self.__plot__(frame, Image("Marked Vehicles", latest, None))
        return latest
