'''
Created on Feb 3, 2017

@author: safdar
'''

import numpy as np
from scipy.ndimage.measurements import label
from sklearn.preprocessing import normalize
from operations.vehicledetection.entities import Candidate
from sklearn.cluster import DBSCAN
import math
from math import sqrt

class ClustererFactory(object):
    @staticmethod
    def create(config):
        clusterer = None
        flavor = list(config.keys())[0]
        if flavor == HeatmapClustererImpl.__name__:
            clusterer = HeatmapClustererImpl(**config[flavor])
        elif flavor == PerspectiveDBSCANClustererImpl.__name__:
            clusterer = PerspectiveDBSCANClustererImpl(**config[flavor])
        elif flavor == ManhattanDBSCANClustererImpl.__name__:
            clusterer = ManhattanDBSCANClustererImpl(**config[flavor])
        else:
            raise "Clusterer not recognized: {}".format(flavor)
        return clusterer

class Clusterer(object):
    def __init__(self, image_shape, min_samples_ratio):
        self.__image_shape__ = image_shape
        self.__min_samples_ratio__ = min_samples_ratio if min_samples_ratio < 1 else 0
        self.__min_samples__ = min_samples_ratio if min_samples_ratio >= 1 else 0
    def clusterandmerge(self, image, boxes):
        raise ("Not implemented")

class HeatmapClustererImpl(Clusterer):
    Structure = [[1,1,1],
                 [1,1,1],
                 [1,1,1]]
    def __init__(self, image_shape, min_samples_ratio):
        Clusterer.__init__(self, image_shape, min_samples_ratio)
    def __add_heat__(self, heatmap, bbox_list, scores):
        # Iterate through list of bboxes
        for box,score in zip(bbox_list, scores):
            # Add += 1 for all pixels inside each bbox
            # Assuming each box takes the form: ((x1,x2),(y1,y2))
            x1,x2,y1,y2 = box.boundary()
            heatmap[y1:y2, x1:x2] += 1
        # Return updated heatmap
        return heatmap
    def __apply_threshold__(self, heatmap, threshold):
        # Zero out pixels below the threshold
        heatmap[heatmap < threshold] = 0
        # Return thresholded map
        return heatmap
    def clusterandmerge(self, candidates):
        mergedcandidates = []
        if candidates is not None and len(candidates) > 0:
            scores = np.array([x.score() for x in candidates])
            scores = (np.array(normalize([scores])*10, dtype=np.uint8)+1)[0] # Convert to 1-11 range.
            heatmap = np.zeros(self.__image_shape__).astype(np.float)
            heatmap = self.__add_heat__(heatmap, candidates, scores)
            minsamples = max([1, self.__min_samples__, len(candidates) * self.__min_samples_ratio__])
            heatmap = self.__apply_threshold__(heatmap, minsamples)
            labels = label(heatmap, structure=HeatmapClustererImpl.Structure)
            for car_number in range(1, labels[1]+1):
                # Find pixels with each car_number label value
                nonzero = (labels[0] == car_number).nonzero()
                # Identify x and y values of those pixels
                nonzeroy = np.array(nonzero[0])
                nonzerox = np.array(nonzero[1])
                # Define a bounding box based on min/max x and y
                x1,y1,x2,y2 = np.min(nonzerox), np.min(nonzeroy), np.max(nonzerox), np.max(nonzeroy)
                center = ((x1+x2)//2, (y1+y2)//2)
                diagonal = sqrt((x2-x1)**2 + (y2-y1)**2)
                mergedcandidate = Candidate.create(center, diagonal, 1)
                mergedcandidates.append(mergedcandidate)
        return mergedcandidates

class DBSCANClustererImpl(Clusterer):
    def __init__(self, image_shape, min_samples_ratio, cluster_range_ratio):
        Clusterer.__init__(self, image_shape, min_samples_ratio)
        self.__cluster_range__ = cluster_range_ratio * np.average(image_shape)
    
class ManhattanDBSCANClustererImpl(DBSCANClustererImpl):
    def __init__(self, image_shape, min_samples_ratio, cluster_range_ratio):
        DBSCANClustererImpl.__init__(self, image_shape, min_samples_ratio, cluster_range_ratio)
    @staticmethod
    def __get_distance__(self, leftbox, rightbox):
        dx = np.absolute(leftbox.center()[0] - rightbox.center()[0])
        dy = np.absolute(leftbox.center()[1] - rightbox.center()[1])
        distance = int(math.sqrt(dx**2 + dy**2))
        return distance
    def clusterandmerge(self, candidates):
        clustered = []
        if candidates is not None and len(candidates) > 0:
            centers = np.array([x.center() for x in candidates], dtype=np.uint32)
            scores = np.array([x.score() for x in candidates])
            scores = (np.array(normalize([scores])*10, dtype=np.uint8)+1)[0] # Convert to 1-11 range.
            minsamples = max([1, self.__min_samples__, len(candidates) * self.__min_samples_ratio__])
            dbscan = DBSCAN(eps=self.__cluster_range__, min_samples=minsamples)
            clusterer = dbscan.fit(centers)
            labels = clusterer.labels_
            
            # Collect the boundary numbers in each cluster:
            clusters = {}
            for i,label in enumerate(labels):
                if label==-1:
                    continue
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(candidates[i])
    
            # Generate a clustered Candidate for each cluster:
            for cluster in clusters:
                clustered.append(Candidate.merge(clusters[cluster]))
        return clustered

class PerspectiveDBSCANClustererImpl(DBSCANClustererImpl):
    def __init__(self, image_shape, min_samples_ratio, cluster_range_ratio):
        DBSCANClustererImpl.__init__(self, image_shape, min_samples_ratio, cluster_range_ratio)
    def __get_distance_matrix__(self, candidates):
        distances = np.full((len(candidates), len(candidates)), fill_value=0, dtype=np.int32)
        for i, leftbox in enumerate(candidates):
            for j, rightbox in enumerate(candidates):
                if i == j:
                    continue
                distances[i][j] = distances[j][i] = self.__get_distance__(leftbox, rightbox)
        return distances
    # This method determines distance between two boxes as being
    # inversely proportional to the box size. The distance between
    # large boxes is the same as the distance in actual pixels.
    # Distance between smaller boxes is inversely proportional
    # to the difference in the size. A small box is far in the horizon. Larger boxes are closer.
    def __get_distance__(self, leftbox, rightbox):
        maxwindow = self.__image_shape__[0]
        # Y-magnification depends on size ratio of the two boxes
        ymagnification = min(rightbox.diagonal()/leftbox.diagonal(), leftbox.diagonal()/rightbox.diagonal())
        # X-magnification depends on the size ratio of small box relative to the biggest box
        xmagnification = maxwindow / min(leftbox.diagonal(), rightbox.diagonal())
        dx = np.absolute(leftbox.center()[0] - rightbox.center()[0]) * xmagnification
        dy = np.absolute(self.__image_shape__[0] * ymagnification) # np.absolute(leftcenter[1] - rightcenter[1]) * ymagnification
        distance = int(math.sqrt(dx**2 + dy**2))
#         print ("Perspective: {} <--> {} : ({}, {})".format(leftbox.diagonal(), rightbox.diagonal(), dx, dy))
        return distance
    def clusterandmerge(self, candidates):
        clustered = []
        if candidates is not None and len(candidates) > 0:
            scores = np.array([x.score() for x in candidates])
            scores = (np.array(normalize([scores])*10, dtype=np.uint8)+1)[0] # Convert to 1-11 range.
            distancemaxtrix = self.__get_distance_matrix__(candidates)
            minsamples = max([1, self.__min_samples__, len(candidates) * self.__min_samples_ratio__])
            dbscan = DBSCAN(eps=self.__cluster_range__, metric='precomputed', min_samples=minsamples)
            clusterer_distance_matrix = dbscan.fit(distancemaxtrix)
            labels_distance_matrix = clusterer_distance_matrix.labels_
            
            if len(labels_distance_matrix) > minsamples:
                print ("Aha...")
            # Collect the boundary numbers in each cluster:
            clusters = {}
            for i,label in enumerate(labels_distance_matrix):
                if label==-1:
                    continue
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(candidates[i])
    
            # Generate a clustered Candidate for each cluster:
            for cluster in clusters:
                clustered.append(Candidate.merge(clusters[cluster]))
        return clustered 