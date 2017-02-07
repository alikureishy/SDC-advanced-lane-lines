'''
Created on Feb 5, 2017

@author: safdar
'''
from operations.vehicledetection.entities import Vehicle
class VehicleManager(object):
    def __init__(self, lookback_frames, clusterer):
        self.__lookback_frames__ = lookback_frames
        self.__vehicles__ = []
        self.__clusterer__ = clusterer

    # Candidate: (center, diagonal, score)
    def add_candidates(self, candidates, continuity_threshold=None):
        existing_vehicles = self.get_vehicles(continuity_threshold=continuity_threshold)
        vehicles_to_add = [Vehicle(candidate.center(), candidate.diagonal(), candidate.score()) for candidate in candidates]
        combined_list = vehicles_to_add + existing_vehicles
#         print ("Existing tracked vehicles: {}".format(len(existing_vehicles)))
#         print ("New tracking candidates: {}".format(len(vehicles_to_add)))
        mergedvehicles = self.__clusterer__.clusterandmerge(combined_list)
#         print ("Post-merge tracked vehicles: {}".format(len(mergedvehicles)))
        self.__vehicles__ = mergedvehicles
        
    def get_vehicles(self, continuity_threshold=None):
        filtered = []
        for vehicle in self.__vehicles__:
            if vehicle.satisfies(continuity_threshold):
                filtered.append(vehicle)
        return filtered
