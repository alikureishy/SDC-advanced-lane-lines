'''
Created on Jan 14, 2017

@author: safdar
'''
import numpy as np

class FeatureCombiner(object):
    def __init__(self, extractors):
        self.__extractors__ = extractors
        
    def extract(self, image):
        featurelist = []
        for extractor in self.__extractors__:
            feature = extractor.extract(image)
            assert feature is not None, "Feature obtained from {} was none".format(extractor.__class__.__name__)
            featurelist.append(feature)
        featurevector = np.concatenate(tuple(featurelist))
        return featurevector
