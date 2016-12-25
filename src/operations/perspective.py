'''
Created on Dec 21, 2016

@author: safdar
'''
from operations.baseoperation import Operation

class Perspective(Operation):
    def __init__(self, params):
        Operation.__init__(params)

    def __processinternal__(self, original, latest, data, plot):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
