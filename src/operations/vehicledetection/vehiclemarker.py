'''
Created on Jan 15, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from operations.vehicledetection.vehicletracker import VehicleTracker
from utils.plotter import Image
import cv2

class DisplayableVehicle(object):
    def __init__(self, vehicle, visible_for):
        self.__vehicle__ = vehicle
        self.__visible_for__ = visible_for
    def visible(self):
        return self.__visible_for__ > 0 and not self.__vehicle__.isdefunct()
    def decay(self):
        self.__visible_for__ -= 1
    def vehicle(self):
        return self.__vehicle__

class VehicleMarker(Operation):
    # Configuration:
    ContinuityThreshold = 'ContinuityThreshold'
    LingerFrames = 'LingerFrames'
    
    # Constants:
    StrongWindowColor = [255, 0, 0]
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__continuity_threshold__ = params[self.ContinuityThreshold]
        self.__linger_frames__ = params[self.LingerFrames]
        self.__display_vehicles__ = []

    def __processdownstream__(self, original, latest, data, frame):
        vehicletracker = self.getdata(data, VehicleTracker.VehicleManager, VehicleTracker)
        
        # Prune visible vehicle list and add the new vehicles to it
        map(lambda x: x.decay(), self.__display_vehicles__)
        self.__display_vehicles__ = [vehicle for vehicle in self.__display_vehicles__ if vehicle.visible()]
        vehicles = vehicletracker.get_vehicles(continuity_threshold=self.__continuity_threshold__)
        for displayable in vehicles:
            self.__display_vehicles__.append(DisplayableVehicle(displayable, self.__linger_frames__))
        
        for displayable in self.__display_vehicles__:
            (x1,x2,y1,y2) = displayable.vehicle().boundary()
            cv2.rectangle(latest, (x1,y1), (x2,y2), self.StrongWindowColor, 3)
            
        if self.isplotting():
            self.__plot__(frame, Image("Marked Vehicles", latest, None))
        return latest
