'''
Created on Feb 3, 2017

@author: safdar
'''
import math
import numpy as np
from math import sqrt
from builtins import staticmethod

class Box(object):
    @staticmethod
    def get_distance(left, right):
        (x1,y1) = left
        (x2,y2) = right
        dx = np.absolute(x2 - x1)
        dy = np.absolute(y2 - y1)
        distance = math.sqrt(dx**2 + dy**2)
        return distance
    
    @staticmethod
    def fromBoundary(upperleft, lowerright):
        x1,y1 = upperleft
        x2,y2 = lowerright
        center = (x1+x2)//2, (y1+y2)//2
        diagonal = Box.get_distance((x1,y2), (x2,y2))
        return Box(center, diagonal)
        
    def __init__(self, center, diagonal, bounds=None):
        assert  (center is not None and diagonal is not None), "Invalid input"
        self.__center__ = center
        self.__diagonal__ = diagonal
        (cx, cy) = self.__center__
        s = int(math.sqrt(((self.__diagonal__ ** 2) / 2)))
        leftx, rightx, topy, bottomy = cx - (s // 2), cx + (s // 2), cy - (s // 2), cy + (s // 2)
        if bounds is not None:
            xrange, yrange=bounds[0], bounds[1]
            if leftx < xrange[0]:
                leftx = xrange[0]
            if rightx > xrange[1]:
                rightx = xrange[1]
            if topy < yrange[0]:
                topy = yrange[0]
            if bottomy > yrange[1]:
                bottomy = yrange[1]
            self.__fitted__ = True
        else:
            self.__fitted__ = False
        assert not (leftx == rightx) or not (topy == bottomy), "Zero sized window found with center: {}, size: {}".format(center, diagonal)
        self.__boundary__ = (leftx, rightx, topy, bottomy)
    def fitted(self):
        return self.__fitted__
    def center(self):
        return self.__center__
    def score(self):
        return self.__score__
    def diagonal(self):
        return self.__diagonal__
    def boundary(self):
        return self.__boundary__
    @staticmethod
    def cluster(boxes):
        return [[]] # Returns a list (rows) of lists (columns). Each row represents one cluster of boxes. 

class Candidate(Box):
    @staticmethod
    def create(center, diagonal, score):
        return Candidate(center, diagonal, score)
    def __init__(self, center, diagonal, score):
        assert  (center is not None and score is not None and diagonal is not None), "Invalid input"
        Box.__init__(self, center, diagonal)
        self.__score__ = score
    def score(self):
        return self.__score__
    def nparray(self):
        return np.array([*self.center(), self.diagonal(), self.score()], dtype=np.int32)
    @staticmethod
    def merge(candidates):
        if len(candidates) == 0:
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            asarray = np.array([x.nparray() for x in candidates])
            # Center is the centroid of the candidates' centers:
            center = np.average(asarray[:,0:2], weights=asarray[:,2], axis=0).astype(np.int32)
            # Instead of being the average, perhaps consider different options. Like
            # the 3*Sigma of the candidates' diagonals?
            diagonal = np.average(asarray[:,2], weights=asarray[:,2], axis=0).astype(np.int32)
            # Score could perhaps also be the 3*Sigma.
            score = np.average(asarray[:,3], axis=0).astype(np.int32) # Only simple average for score
            mergedcandidate = Candidate(center, diagonal, score)
            mergedcandidate.__merged__ = True
            return mergedcandidate

# class Vehicle(Candidate):
#     @staticmethod
#     def create(center, score, diagonal, lookback):
#         return Vehicle(center, score, diagonal, lookback)
#     def __init__(self, center, score, diagonal, lookback=5):
#         Candidate.__init__(self, center, score, diagonal)
#         self.__lookback__ = lookback
#         self.__history__ = np.empty((0, 4), dtype=np.int32)
#         self.__continuous_hits__ = 0
#         self.__continuous_misses__ = 0
#         self.__hits__ = 0
#         self.__misses__ = 0
#         self.__merged__ = False
#     def hit(self, detection):
#         self.__hits__ += 1
#         self.__continuous_hits__ += 1
#         self.__continuous_misses__ = 0
#         self.addlocation(detection)
#     def miss(self):
#         self.__misses__ += 1
#         self.__continuous_hits__ = 0
#         self.__continuous_misses__ += 1
# #         self.addlocation(detection=None)
# #     def addlocation(self, detection=None):
# #         if detection is None:
# #             if len(self.__history__) > 0:
# #                 self.__history__ = np.append(self.__history__, [self.__history__[-1]], axis=0)
# #         else:
# #             self.__history__ = np.append(self.__history__, [detection.nparray()], axis=0)
# #         if len(self.__history__) > self.__lookback__:
# #             self.__history__ = np.delete(self.__history__, 0, axis=0)
# #         self.__center__ = np.average(self.__history__[:,0], weights=self.__history__[:,2], axis=0).astype(np.int32)
# #         self.__diagonal__ = np.average(self.__history__[:,1], weights=self.__history__[:,2], axis=0).astype(np.int32)
# #         self.__score__ = np.average(self.__history__[:,2], axis=0).astype(np.int32) # Only simple average for score
#     def projected_gap(self, detection, frames=1):
#         projected = self.project(frames=frames)
#         if projected is not None:
#             (x1,y1) = projected.center()
#             (x2,y2) = detection.center()
#             distance = int(sqrt((x1-x2)**2 + (y1-y2)**2))
#             gap = distance - (projected.diagonal()/2 + detection.diagonal()/2)
#             return gap
#         return None
#     def project(self, frames=1):
#         return self # Eventually return a Candidate instance that is predicted by a Kalman filter
#     def continuous_hits(self):
#         return self.__continuous_hits__
#     def continuous_misses(self):
#         return self.__continuous_misses__
#     def hits(self):
#         return self.__hits__
#     def misses(self):
#         return self.__misses__
#     def location_history(self):
#         return self.__history__[:,0:2]
#     def isdefunct(self):
#         return self.__misses__ > self.__hits__
#     def makedefunct(self):
#         self.__misses__ = 1
#         self.__hits__ = -1
#     def wasmerged(self):
#         return self.__merged__
#     def age(self):
#         return self.__hits__ + self.__misses__
#     def satisfies(self, continuity_threshold=None):
#         return not self.isdefunct() and (continuity_threshold is None or self.continuous_hits() >= continuity_threshold)
#     def nparray(self):
#         return np.array([*Candidate.nparray(self), self.hits(), self.continuous_hits(), self.misses(), self.continuous_misses()])
#     @staticmethod
#     def merge(vehicles):
#         if len(vehicles) == 0:
#             return None
#         elif len(vehicles) == 1:
#             if vehicles[0].age() > 0:
#                 vehicles[0].miss() # Register a miss because this vehicle hasn't been merged with a new location
#             return vehicles[0]
#         else:
#             asarray = np.array([x.nparray() for x in vehicles])
#             center = np.average(asarray[:,0:2], weights=asarray[:,2], axis=0).astype(np.int32)
#             # Consider 3*Sigma again, or perhaps stick with average?
#             diagonal = np.average(asarray[:,2], weights=asarray[:,2], axis=0).astype(np.int32)
#             score = np.average(asarray[:,3], axis=0).astype(np.int32) # Only simple average for score
#             hits = np.max(asarray[:,4]).astype(np.int32)
#             conthits = np.max(asarray[:,5]).astype(np.int32)
#             misses = np.max(asarray[:,6]).astype(np.int32)
#             map(lambda x: x.makedefunct(), vehicles)
#             mergedvehicle = Vehicle(center, diagonal, score)
#             mergedvehicle.__hits__ = hits + 1
#             mergedvehicle.__continuous_hits__ = conthits + 1
#             mergedvehicle.__misses__ = misses
#             mergedvehicle.__continuous_misses__ = 0
#             mergedvehicle.__merged__ = True
#             return mergedvehicle
