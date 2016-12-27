'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation

class ShowOriginal(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processinternal__(self, original, latest, data, frame):
        frame.add(original, None, "Original", None)
        return latest
