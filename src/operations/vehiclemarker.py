'''
Created on Jan 15, 2017

@author: safdar
'''

from operations.baseoperation import Operation

class VehicleMarker(Operation):
    # Configuration:
    CurrentBoundingBoxColor = 'CurrentBoundingBoxColor'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__bounding_box_color__ = params[self.CurrentBoundingBoxColor]

    def __processupstream__(self, original, latest, data, frame):
        return latest

    def __processdownstream__(self, original, latest, data, frame):
        return latest
