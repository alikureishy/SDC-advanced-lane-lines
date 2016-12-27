'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation

class LaneFiller(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processinternal__(self, original, latest, data, frame):
        raise "Not implemented"
        