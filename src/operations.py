'''
Created on Dec 22, 2016

@author: safdar
'''
import pickle

# Fixed Sequence:
# - Undistorter
# - Thresholder
# - Perspective
# - LaneMapper
# -     LaneFiller

class Operation(object):
    # Parameters
    IsPlotting = 'Show'
    
    # Data items:
    Original = 'Original'
    
    #TODO: Rewire this to read a section, rather than an option string
    def __init__(self, options):
        self.__options__ = options

    def process(self, original, processed, data, plot):
        processed = self.processinternal(original, processed, data, plot)
        processed = self.__succesor__.process(original, processed, data, plot)

    def setsuccessor(self, successor):
        self.__successor__ = successor

    def __processinternal__(self):
        raise "Not implemented"

    def getparam(self, paramname):
        return self.__options__[paramname]
    
    def getintparam(self, paramname):
        return int(self.getparam(paramname)) 
    
    def getboolparam(self, paramname):
        return bool(self.getparam(paramname)) 

    def getfloatparam(self, paramname):
        return float(self.getparam(paramname)) 

    def getinttupleparam(self, paramname):
        raise "Not implemented" # Need to use a regular expression to parse '( .. , .. )'

    def getfloattupleparam(self, paramname):
        raise "Not implemented"

    def isplotting(self):
        return bool(self.__options__[self.IsPlotting])

    def plotcount(self):
        if self.isplotting():
            return self.__plotcount__()
        else:
            return 0

    def __plotcount__(self):
        raise "Abstract method. Check instance type."


class Calibrator(Operation):
    # Parameters
    CalibrationFile = 'CalibrationFile'
    MTX = 'features'
    DIST = "dist"
    
    def __init__(self, params):
        Operation.__init__(params)
        file = self.getparam(self.CalibrationFile)
        with open(file, mode='rb') as f:
            calibration_data = pickle.load(f)
            self.__mtx__ = calibration_data[self.MTX]
            self.__dist__ = calibration_data[self.DIST]

    def __processinternal__(self):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
    
class RegionMasker(Operation):
    def __init__(self, params):
        Operation.__init__(params)

    def __processinternal__(self):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
    
class Thresholder(Operation):
    def __init__(self, params):
        Operation.__init__(params)

    def __processinternal__(self):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
    
class Perspective(Operation):
    def __init__(self, params):
        Operation.__init__(params)

    def __processinternal__(self):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
    
# Detects and fits the lane points, then fills the region between the fitted polynomials    
class LaneMapper(Operation):
    def __init__(self, params):
        Operation.__init__(params)

    def __processinternal__(self):
        raise "Not implemented"

    def __plotcount__(self):
        raise "Not implemented"
    
# class Canny(Operation):
#     def __init__(self, params):
#         raise "Not implemented"
# 
# class Hough(Operation):
#     def __init__(self, params):
#         raise "Not implemented"

# class Selector(object):
#     def __init__(self, params):
#         raise "Not implemented"


#self.__options__ = {setting[0]:setting[1] for setting in [option.split('=', 1) for option in optionstring.split(';')]}

