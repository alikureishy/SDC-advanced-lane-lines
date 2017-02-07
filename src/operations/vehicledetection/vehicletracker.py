'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
from operations.vehicledetection.vehiclefinder import VehicleFinder
import numpy as np
from utils.plotter import Image
import cv2
from operations.vehicledetection.vehicleclusterer import VehicleClusterer
from operations.vehicledetection.tracker import VehicleManager
from operations.vehicledetection.clusterers import ClustererFactory


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
    VehicleWindowColor = [255, 0, 0]
    MergedVehicleColor = [155, 0, 0]
    
    # Outputs:
    VehicleManager = 'VehicleManager'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__vehicle_manager__ = None
        self.__clusterer__ = None

    def __processupstream__(self, original, latest, data, frame):
        if self.__vehicle_manager__ is None:
            config = self.getparam(self.Clusterer)
            config[list(config.keys())[0]]['image_shape'] = latest.shape[0:2]
            self.__clusterer__ = ClustererFactory.create(config)
            self.__vehicle_manager__ = VehicleManager(self.getparam(self.LookBackFrames), self.__clusterer__)
        
        # Candidate: (center, diagonal, score)
        detections = self.getdata(data, VehicleClusterer.ClusterCandidates, VehicleClusterer)
        self.__vehicle_manager__.add_candidates(detections, continuity_threshold=4)

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
        