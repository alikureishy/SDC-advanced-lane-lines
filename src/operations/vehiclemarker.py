'''
Created on Jan 15, 2017

@author: safdar
'''

from operations.baseoperation import Operation

class VehicleMarker(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        return latest
