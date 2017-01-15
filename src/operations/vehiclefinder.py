'''
Created on Jan 14, 2017

@author: safdar
'''

from operations.baseoperation import Operation
from sklearn.externals import joblib
from extractors.colorhistogram import ColorHistogram
from extractors.spatialbinner import SpatialBinner
from extractors.hogextractor import HogExtractor
from extractors.featurecombiner import FeatureCombiner

class VehicleFinder(Operation):
    ClassifierFile = 'ClassifierFile'
    FeatureExtractors = 'FeatureExtractors'
    class Term(object):
        ToPlot = 'ToPlot'
    class SpatialBinning(Term):
        Space = 'Space'
        Size = 'Size'
    class ColorHistogram(Term):
        Space = 'Space'
        NumBins = 'NumBins'
        BinRange = 'BinRange'
    class HOGExtractor(Term):
        Orientations = 'Orientations'
        HogChannel = 'HogChannel'
        PixelsPerCell = 'PixelsPerCell'
        CellsPerBlock = 'CellsPerBlock'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__classifier__ = joblib.load(params[self.ClassifierFile])
        sequence = params[self.FeatureExtractors]
        extractors = []
        for config in sequence:
            assert len(config.keys())==1, "Invalid: {}".format(config)
            extractor = None
            if self.ColorHistogram.__name__ in config:
                cfg = config[self.ColorHistogram.__name__]
                extractor = ColorHistogram(color_space=cfg[self.ColorHistogram.Space], 
                                           nbins=cfg[self.ColorHistogram.NumBins], 
                                           bins_range=cfg[self.ColorHistogram.BinRange])
            elif self.SpatialBinning.__name__ in config:
                cfg = config[self.SpatialBinning.__name__]
                extractor = SpatialBinner(color_space=cfg[self.SpatialBinning.Space],
                                          size=cfg[self.SpatialBinning.Size])
            elif self.HOGExtractor.__name__ in config:
                cfg = config[self.HOGExtractor.__name__]
                extractor = HogExtractor(orientations=cfg[self.HOGExtractor.Orientations],
                                          hog_channel=cfg[self.HOGExtractor.HogChannel],
                                          pixels_per_cell=cfg[self.HOGExtractor.PixelsPerCell],
                                          cells_per_block=cfg[self.HOGExtractor.CellsPerBlock])
            else:
                raise ("Unrecognized extractor provided")
            extractors.append(extractor)
        self.__combiner__ = FeatureCombiner(tuple(extractors))

    def __processupstream__(self, original, latest, data, frame):
        return latest
