'''
Created on Dec 22, 2016

@author: safdar
'''
class Operation(object):
    # Parameters
    IsPlotting = 'ToPlot'
    
    # Data items:
    Original = 'Original'
    
    def __init__(self, options):
        self.__options__ = options

    def process(self, original, latest, data, plot):
        intermediate = self.processinternal(original, latest, data, plot)
        final = self.__succesor__.process(original, intermediate, data, plot)
        return final

    def setsuccessor(self, successor):
        self.__successor__ = successor

    def __processinternal__(self,original, latest, data, plot):
        raise "Not implemented"

    def getparam(self, paramname):
        return self.__options__[paramname]
    
    def getintparam(self, paramname):
        return int(self.getparam(paramname)) 
    
    def getboolparam(self, paramname):
        return bool(self.getparam(paramname)) 

    def getfloatparam(self, paramname):
        return float(self.getparam(paramname)) 

    def gettupleparam(self, paramname):
        raise "Not implemented" # Need to use a regular expression to parse '( .. , .. )'
        
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

