'''
Created on Jan 14, 2017

@author: safdar
'''

import numpy as np
import cv2
from scipy.ndimage.measurements import label
from operations.baseoperation import Operation
from numpy import mean
from operations.vehiclefinder import VehicleFinder
from utils.plotter import Image

class VehicleLabeler(Operation):
    HeatmapThreshold = 'HeatmapThreshold'

    # Constants:
    BoxColor = [0,0,255]

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__heatmap_threshold__ = params[self.HeatmapThreshold]

    @staticmethod
    def add_heat(heatmap, bbox_list):
        # Iterate through list of bboxes
        for box in bbox_list:
            # Add += 1 for all pixels inside each bbox
            # Assuming each box takes the form: ((x1,x2),(y1,y2))
            x1,x2,y1,y2 = box.boundary()
            heatmap[y1:y2, x1:x2] += 1
        # Return updated heatmap
        return heatmap
        
    @staticmethod
    def apply_threshold(heatmap, threshold):
        # Zero out pixels below the threshold
        heatmap[heatmap < threshold] = 0
        # Return thresholded map
        return heatmap

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim, xy_avg = latest.shape[1], latest.shape[0], int(mean(latest.shape[0:2]))

        framecandidates = self.getdata(data, VehicleFinder.FrameCandidates, VehicleFinder)
        heatmap = np.zeros_like(latest[:,:,0]).astype(np.float)
        heatmap = VehicleLabeler.add_heat(heatmap, framecandidates)
        heatmap = VehicleLabeler.apply_threshold(heatmap, self.__heatmap_threshold__)
        labels = label(heatmap)
        
        if self.isplotting():
            
            # First plot the heatmaps:
            self.__plot__(frame, Image("Heatmap", heatmap, 'gray'))
            
            # Then plot the labels:
            self.__plot__(frame, Image("Cars found: {}".format(labels[1]), labels[0], 'gray'))
            
            # Then draw the bounding boxes around the labeled sections:
            labeled = np.copy(latest)
            for car_number in range(1, labels[1]+1):
                # Find pixels with each car_number label value
                nonzero = (labels[0] == car_number).nonzero()
                # Identify x and y values of those pixels
                nonzeroy = np.array(nonzero[0])
                nonzerox = np.array(nonzero[1])
                # Define a bounding box based on min/max x and y
                bbox = ((np.min(nonzerox), np.min(nonzeroy)), (np.max(nonzerox), np.max(nonzeroy)))
                # Draw the box on the image
                cv2.rectangle(labeled, bbox[0], bbox[1], self.BoxColor, 6)
            self.__plot__(frame, Image("Labeled Cars", labeled, None))
        
        return latest
