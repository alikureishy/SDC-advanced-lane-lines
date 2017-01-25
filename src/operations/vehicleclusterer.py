'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from operations.vehiclefinder import VehicleFinder
from math import sqrt
import numpy as np
from utils.plotter import Image

import math
import cv2

class VehicleClusterer(Operation):
    # Configuration:
#     Perspective = 'Perspective'
#     DepthRangeRatio = 'DepthRangeRatio'
    ClusterRangeRatio = 'ClusterRangeRatio'
    
    # Outputs:
    ClusterVehicles = 'ClusterVehicles'
    ClusterBoxes = 'ClusterBoxes'
    
    # Constants:
    StrongWindowColor = [255, 0, 0]
    
    def __init__(self, params):
        Operation.__init__(self, params)
#         self.__perspective__ = params[self.Perspective]
#         self.__depth_range_ratios__ = params[self.DepthRangeRatio]
        self.__cluster_range__ratio = params[self.ClusterRangeRatio]
        self.__cluster_range__ = None
        

    def get_distance(self, left, right):
        (x1,x2,y1,y2) = left
        leftcenter = ((x1+x2)//2, (y1+y2)//2)
        (p1,p2,q1,q2) = right
        rightcenter = ((p1+p2)//2, (q1+q2)//2)
        dx = np.absolute(leftcenter[0] - rightcenter[0])
        dy = np.absolute(leftcenter[1] - rightcenter[1])
        distance = math.sqrt(dx**2 + dy**2)
        return distance

    def get_distance_matrix(self, boxes):
        distances = [[0 for _ in range(len(boxes))] for __ in range(len(boxes))]
        for i, (leftbox, _) in enumerate(boxes):
            for j, (rightbox, _) in enumerate(boxes):
                if i == j:
                    continue
                distances[i][j] = distances[j][i] = self.get_distance(leftbox, rightbox)
        return distances

    def get_center_and_diagonal(self, boxcorners):
        (x1,x2,y1,y2) = boxcorners
        center = ((x1+x2)//2, (y1+y2)//2)
        diagonal = int(sqrt((x1-x2)**2 + (y1-y2)**2))
#         diagonal = euclidean((x1,y1), (x2,y2))
        return center, diagonal
    
    def get_centers(self, detections):
        boxes, _ = tuple(zip(*detections))
        centers = []
        for boxnumber,box in enumerate(boxes):
            center,_ = self.get_center_and_diagonal(box)
            centers.append((center, boxnumber))
        return centers
    
    def __processupstream__(self, original, latest, data, frame):
        if self.__cluster_range__ is None:
            self.__cluster_range__ = int(self.__cluster_range__ratio * (np.average(latest.shape[0:2])))
        
        detections = self.getdata(data, VehicleFinder.FrameVehicleDetections, VehicleFinder)
        cluster_boxes = []
        cluster_vehicles = []
        if detections is not None:
            boxes, scores = tuple(zip(*detections))
            scores = (np.array(normalize([scores])*10, dtype=np.uint8)+1)[0] # Convert to 1-11 range.
            centers,boxnumbers = tuple(zip(*self.get_centers(detections)))
            assert len(centers) == len(boxnumbers)

            # Do the clustering:
            centers = np.array(list(centers))
            dbscan = DBSCAN(eps=self.__cluster_range__, min_samples=min(scores))
            clusterer = dbscan.fit(centers, sample_weight=scores)
            labels = clusterer.labels_
            
            # Collect the box numbers in each cluster:
            clusters = {}
            for boxnumber, label in zip(boxnumbers, labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(boxnumber)

            # Generate box for each cluster:
            for cluster in clusters:
                ids = clusters[cluster]
                centers, diagonals = [], []
                for i in ids:
                    center,diagonal = self.get_center_and_diagonal(boxes[i])
                    centers.append(center)
                    diagonals.append(diagonal)
                cx,cy = tuple(np.average(centers, axis=0, weights=scores[ids]).astype(np.uint16))
                diagonal = np.average(diagonals, weights=scores[ids])
                cluster_vehicles.append(((cx,cy), diagonal, sum(scores[ids])))

                # Generate new box:
                s = int(math.sqrt(((diagonal**2)/2)))
                box = (cx-(s//2), cx+(s//2), cy+(s//2), cy-(s//2)) 
                cluster_boxes.append(box)
            self.setdata(data, self.ClusterBoxes, cluster_boxes)
            self.setdata(data, self.ClusterVehicles, cluster_vehicles)

        if self.isplotting():
            clustered = np.copy(latest)
            for (x1,x2,y1,y2) in cluster_boxes:
                cv2.rectangle(clustered, (x1,y1), (x2,y2), self.StrongWindowColor, 2)
            self.__plot__(frame, Image("Clustered Vehicles", clustered, None))
        return latest
        