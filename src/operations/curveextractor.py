'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
    
# Detects and fits the lane points, then fills the region between the fitted polynomials    
class CurveExtractor(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processinternal__(self, original, latest, data, frame):
        return latest
