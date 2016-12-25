'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation

class LaneFiller(Operation):
    def __init__(self, params):
        Operation.__init__(params)

    def __processinternal__(self, original, latest, data, plot):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
        