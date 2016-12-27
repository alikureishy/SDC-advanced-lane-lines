'''
Created on Dec 23, 2016

@author: safdar
'''
import cv2
from operations.baseoperation import Operation
import pickle

class Undistorter(Operation):
    # Parameters
    CalibrationFile = 'CalibrationFile'
    MTX = 'mtx'
    DIST = "dist"
    
    def __init__(self, params):
        Operation.__init__(self, params)
        file = self.getparam(self.CalibrationFile)
        with open(file, mode='rb') as f:
            calibration_data = pickle.load(f)
            self.__mtx__ = calibration_data[self.MTX]
            self.__dist__ = calibration_data[self.DIST]

    def __processinternal__(self, original, latest, data, frame):
        undistorted = cv2.undistort(latest, self.__mtx__, self.__dist__, None, self.__mtx__)
        self.__plot__(frame, undistorted, None, "Undistorter", None)
        return undistorted
