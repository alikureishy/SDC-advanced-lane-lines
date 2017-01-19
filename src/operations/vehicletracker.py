'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation

class VehicleTracker(Operation):
    # Configuration:
    HardFalsePositivesDump = 'HardFalsePositivesDump'
    HardFalseNegativesDump = 'HardFalseNegativesDump'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__hard_false_positives__ = params[self.HardFalsePositivesDump]
        self.__hard_false_negatives__ = params[self.HardFalseNegativesDump]

    def __processupstream__(self, original, latest, data, frame):
        return latest
        