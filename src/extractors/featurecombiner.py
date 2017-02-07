'''
Created on Jan 14, 2017

@author: safdar
'''
import numpy as np
from sklearn.preprocessing.data import StandardScaler

class FeatureCombiner(object):
    def __init__(self, extractors):
        self.__extractors__ = extractors
        
    def extract(self, image):
        featurelist = []
        for extractor in self.__extractors__:
            feature = extractor.extract(image)
            assert feature is not None, "Feature obtained from {} was none".format(extractor.__class__.__name__)
            featurelist.append(feature)
        features = np.concatenate(tuple(featurelist))
        scaled_features = StandardScaler().fit_transform(features.reshape(-1,1))
        #scaled_features = scaled_features.reshape(1, -1)
        scaled_features = scaled_features.ravel()
        
        return scaled_features
