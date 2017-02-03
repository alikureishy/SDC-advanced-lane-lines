'''
Created on Dec 22, 2016

@author: safdar
'''
from operations.undistorter import Undistorter
from operations.thresholder import Thresholder
from operations.perspectivetransformer import PerspectiveTransformer
from operations.lanefiller import LaneFiller
from operations.showoriginal import ShowOriginal
from operations.lanefinder import LaneFinder
from operations.perspectivefinder import PerspectiveFinder
from operations.statswriter import StatsWriter
from operations.vehiclefinder import VehicleFinder
from operations.vehicleclusterer import VehicleClusterer
from operations.vehicletracker import VehicleTracker
from operations.vehiclemarker import VehicleMarker
from operations.vehiclelabeler import VehicleLabeler

PipelineSection = 'Pipeline'
# from operations import *

class Pipeline(object):
    def __init__(self, config, selector=None):
        self.__config__ = config
        self.__operations__ = []
        self.__data__ = {}
        if selector is None:
            self.__sequence__ = config[PipelineSection]
        else:
            if not 0<selector<=len(config[PipelineSection]):
                raise "Selector value of {} was not valid. Must be [1..{}]".format(selector, len(config[PipelineSection]))
            self.__sequence__ = config[PipelineSection][0:selector]

        for operation in self.__sequence__:
            op = self.__create_operation__(operation, config[operation])
            if len(self.__operations__)>0:
                self.__operations__[-1].setsuccessor(op)
            self.__operations__.append(op)
    
    def __create_operation__(self, name, config):
        instance = None
        if name == ShowOriginal.__name__:
            return ShowOriginal(config)
        elif name == StatsWriter.__name__:
            return StatsWriter(config)
        elif name == Undistorter.__name__:
            return Undistorter(config)
        elif name == VehicleFinder.__name__:
            return VehicleFinder(config)
        elif name == VehicleLabeler.__name__:
            return VehicleLabeler(config)
        elif name == VehicleClusterer.__name__:
            return VehicleClusterer(config)
        elif name == VehicleTracker.__name__:
            return VehicleTracker(config)
        elif name == VehicleMarker.__name__:
            return VehicleMarker(config)
        elif name == Thresholder.__name__:
            return Thresholder(config)
        elif name == PerspectiveFinder.__name__:
            return PerspectiveFinder(config)
        elif name == PerspectiveTransformer.__name__:
            return PerspectiveTransformer(config)
        elif name == LaneFinder.__name__:
            return LaneFinder(config)
        elif name == LaneFiller.__name__:
            return LaneFiller(config)
        else:
            raise ValueError("No operation class exists with name: {}".format(name))
        return instance
        
    def execute(self, image, frame):
        processed = None
        if len(self.__operations__)>0:
            processed = self.__operations__[0].process(image, image, self.__data__, frame)
        return processed