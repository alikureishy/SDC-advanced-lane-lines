'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation

class LaneFiller(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        return latest
        