'''
Created on Jan 15, 2017

@author: safdar
'''
from operations.baseoperation import Operation
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from operations.vehiclefinder import VehicleFinder, Box, Candidate
import numpy as np
from utils.plotter import Image

import math
import cv2

class VehicleClusterer(Operation):
    # Configuration:
#     Perspective = 'Perspective'
#     DepthRangeRatio = 'DepthRangeRatio'
    ClusterRangeRatio = 'ClusterRangeRatio'
    MinSamplesRatio = 'MinSamplesRatio'
    
    # Outputs:
    ClusterCandidates = 'ClusterCandidates'
    
    # Constants:
    StrongWindowColor = [255, 0, 0]
    
    def __init__(self, params):
        Operation.__init__(self, params)
#         self.__perspective__ = params[self.Perspective]
#         self.__depth_range_ratios__ = params[self.DepthRangeRatio]
        self.__heatmap_threshold__ = params[self.ClusterRangeRatio]
        self.__cluster_range__ = None
        self.__min_samples_ratio__ = params[self.MinSamplesRatio]

    def get_distance(self, left, right):
        (x1,x2,y1,y2) = left
        leftcenter = ((x1+x2)//2, (y1+y2)//2)
        (p1,p2,q1,q2) = right
        rightcenter = ((p1+p2)//2, (q1+q2)//2)
        dx = np.absolute(leftcenter[0] - rightcenter[0])
        dy = np.absolute(leftcenter[1] - rightcenter[1])
        distance = math.sqrt(dx**2 + dy**2)
        return distance

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim = latest.shape[1], latest.shape[0]
        if self.__cluster_range__ is None:
            self.__cluster_range__ = int(self.__heatmap_threshold__ * (np.average(latest.shape[0:2])))
        
        framecandidates = self.getdata(data, VehicleFinder.FrameCandidates, VehicleFinder)
        windowrange = self.getdata(data, VehicleFinder.WindowSizeRange, VehicleFinder)
        
        candidates = []
        if framecandidates is not None and len(framecandidates) > 0:
            framecandidates = np.array(framecandidates)
            scores = np.array([x.score() for x in framecandidates])
            scores = (np.array(normalize([scores])*10, dtype=np.uint8)+1)[0] # Convert to 1-11 range.
            centers = np.array([x.center() for x in framecandidates], dtype=np.uint32)

            # Do the clustering:
            distancemaxtrix = Box.get_distance_matrix(framecandidates, (x_dim, y_dim), windowrange)
            minsamples = len(centers) * self.__min_samples_ratio__ if self.__min_samples_ratio__ is not None else None
            dbscan = DBSCAN(eps=self.__cluster_range__, min_samples=minsamples)
            dbscan_distance_matrix = DBSCAN(eps=self.__cluster_range__, metric='precomputed', min_samples=minsamples)
            clusterer = dbscan.fit(centers, sample_weight=scores)
            clusterer_distance_matrix = dbscan_distance_matrix.fit(distancemaxtrix, sample_weight=scores)
            labels = clusterer.labels_
            labels_distance_matrix = clusterer_distance_matrix.labels_
            
            # Collect the boundary numbers in each cluster:
            clusters = {}
            for i,label in enumerate(labels_distance_matrix):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(framecandidates[i])

            # Generate a clustered Candidate for each cluster:
            for cluster in clusters:
                candidates.append(Candidate.merge(clusters[cluster]))
            self.setdata(data, self.ClusterCandidates, candidates)

        if self.isplotting():
            clustered = np.copy(latest)
            for candidate in candidates:
                (x1,x2,y1,y2) = candidate.boundary()
                cv2.rectangle(clustered, (x1,y1), (x2,y2), self.StrongWindowColor, 2)
            self.__plot__(frame, Image("Clustered Candidates", clustered, None))
        return latest
        