'''
Created on Dec 22, 2016

@author: safdar
'''
from operations.undistorter import Undistorter
from operations.thresholder import Thresholder
from operations.regionmasker import RegionMasker
from operations.perspective import Perspective
from operations.lanefiller import LaneFiller
from operations.curveextractor import CurveExtractor
from operations.showoriginal import ShowOriginal
from operations.resizer import Resizer

PipelineSection = 'Pipeline'
# from operations import *

class Pipeline(object):
    def __init__(self, config, selector=None):
        self.__config__ = config
        self.__operations__ = []
        if selector is None:
            self.__sequence__ = config[PipelineSection]
        else:
            self.__sequence__ = ['ShowOriginal', selector]

        for operation in self.__sequence__:
            op = self.__create_operation__(operation, config[operation])
            if len(self.__operations__)>0:
                self.__operations__[-1].setsuccessor(op)
            self.__operations__.append(op)
    
    def __create_operation__(self, name, config):
        instance = None
        if name == 'ShowOriginal':
            return ShowOriginal(config)
        elif name == 'Resizer':
            return Resizer(config)
        elif name == 'Undistorter':
            return Undistorter(config)
        elif name == 'Thresholder':
            return Thresholder(config)
        elif name == 'RegionMasker':
            return RegionMasker(config)
        elif name == 'Perspective':
            return Perspective(config)
        elif name == 'CurveExtractor':
            return CurveExtractor(config)
        elif name == 'LaneFiller':
            return LaneFiller(config)
        else:
            raise "No operation class exists with name: {}".format(name)   
            
        # It is possible this portion will change, depending on how the config references the operation:
#         import importlib
#         module_name, class_name = "operations", name
#         MyClass = getattr(importlib.import_module(module_name), class_name)
#         instance = MyClass(optionstring)

#         klass = globals()[name]
#         instance = klass(optionstring)
#         instance = name(config)
        
        return instance
        
    def execute(self, image, frame):
        processed = None
        if len(self.__operations__)>0:
            data = {}
            processed = self.__operations__[0].process(image, image, data, frame)
        return processed