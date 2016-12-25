'''
Created on Dec 23, 2016

@author: safdar
'''
import cv2
from operations.baseoperation import Operation
import pickle

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

    def __processinternal__(self, original, latest, data, plot):
        assert latest==None, "This should be the first item in the pipeline"
        undistorted = cv2.undistort(original, self.__mtx__, self.__dist__, None, self.__mtx__)
        plot.add(undistorted)
        return undistorted

    def __plotcount__(self):
        return 1
