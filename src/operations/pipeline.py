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
from operations.colorspacer import ColorSpacer

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
        elif name == ColorSpacer.__name__:
            return ColorSpacer(config)
        elif name == Resizer.__name__:
            return Resizer(config)
        elif name == Undistorter.__name__:
            return Undistorter(config)
        elif name == Thresholder.__name__:
            return Thresholder(config)
        elif name == RegionMasker.__name__:
            return RegionMasker(config)
        elif name == Perspective.__name__:
            return Perspective(config)
        elif name == CurveExtractor.__name__:
            return CurveExtractor(config)
        elif name == LaneFiller.__name__:
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
            processed = self.__operations__[0].process(image, image, self.__data__, frame)
        return processed