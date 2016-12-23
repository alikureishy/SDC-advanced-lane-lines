'''
Created on Dec 22, 2016

@author: safdar
'''

Pipeline = '[Pipeline]'

class Chain(object):
    '''
    params is a ConfigParser object, already initialized with the config file.
    '''
    def __init__(self, config):
        self.__config__ = config
        self.__operations__ = []
        self.__plotcount__ = 0
        for operation in config.items(Pipeline):
            op = self.__create_operation__(operation, config[operation])
            if len(self.__operations__)>0:
                self.__operations__[-1].setsuccessor(op)
            self.__operations__.append(op)
            self.__plotcount__ += op.plotcount()

    def plotcount(self):
        return self.__plotcount__
    
    def __create_operation__(self, name, optionstring):
        import importlib
#         module_name, class_name = "module.submodule.Klass".rsplit(".", 1)
        module_name, class_name = "operations", name
        MyClass = getattr(importlib.import_module(module_name), class_name)
        instance = MyClass(optionstring)
        return instance
        
    def execute(self, image, plot):
        processed = None
        if len(self.__operations__)>0:
            data = {}
            processed = self.__operations__[0].process(image, image, data, plot)
        return processed