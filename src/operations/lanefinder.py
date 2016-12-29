'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
    
# Detects the points on each lane and fits each with a polynomial function
# Also detects the position of the car relative to the center of the lane,
# based on the lane positions.
class LaneFinder(Operation):
    
    
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        return latest
