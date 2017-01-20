'''
Created on Dec 26, 2016

@author: safdar
'''
from operations.baseoperation import Operation
from utils.plotter import Image
from utils.plotter import Graph

class ShowOriginal(Operation):
    def __init__(self, params):
        Operation.__init__(self, params)

    def __processupstream__(self, original, latest, data, frame):
        self.__plot__(frame, Image("Original: {}".format(original.shape), original, None))
        return latest
