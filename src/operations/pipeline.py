'''
Created on Dec 22, 2016

@author: safdar
'''

Pipeline = '[Pipeline]'

class Pipeline(object):
    def __init__(self, config, selector=None):
        self.__config__ = config
        self.__operations__ = []
        self.__sequence__ = config[Pipeline]
        if selector is None:
            for operation in self.__sequence__:
                op = self.__create_operation__(operation, config[operation])
                if len(self.__operations__)>0:
                    self.__operations__[-1].setsuccessor(op)
                self.__operations__.append(op)
        else:
            if not selector in config:
                raise "Selected operation {} does not exist in the conguration file {}".format(selector)
            op = self.__create_operation__(selector, config[selector])
            self.__operations__.append(op)

    def plotcount(self):
        return self.__plotcount__
    
    def __create_operation__(self, name, optionstring):
        # It is possible this portion will change, depending on how the config references the operation:
        import importlib
        module_name, class_name = "operations.baseoperation", name
        MyClass = getattr(importlib.import_module(module_name), class_name)
        instance = MyClass(optionstring)
        
        return instance
        
    def execute(self, image, plot):
        processed = None
        if len(self.__operations__)>0:
            data = {}
            processed = self.__operations__[0].process(image, None, data, plot)
        return processed