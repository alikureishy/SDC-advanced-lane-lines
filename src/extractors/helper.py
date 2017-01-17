'''
Created on Jan 16, 2017

@author: safdar
'''
from extractors.colorhistogram import ColorHistogram
from extractors.spatialbinner import SpatialBinner
from extractors.hogextractor import HogExtractor
from extractors.featurecombiner import FeatureCombiner

class Types(object):
    class SpatialBinning(object):
        Space = 'Space'
        Size = 'Size'
    class ColorHistogram(object):
        Space = 'Space'
        NumBins = 'NumBins'
        BinRange = 'BinRange'
    class HOGExtractor(object):
        Orientations = 'Orientations'
        HogChannel = 'HogChannel'
        PixelsPerCell = 'PixelsPerCell'
        CellsPerBlock = 'CellsPerBlock'
        Size = 'Size'
    
def buildextractor(extractorsequence):
    extractors = []
    for config in extractorsequence:
        assert len(config.keys()) == 1, "Invalid: {}".format(config)
        extractor = None
        if Types.ColorHistogram.__name__ in config:
            cfg = config[Types.ColorHistogram.__name__]
            extractor = ColorHistogram(color_space=cfg[Types.ColorHistogram.Space], nbins=cfg[Types.ColorHistogram.NumBins], 
                bins_range=cfg[Types.ColorHistogram.BinRange])
        elif Types.SpatialBinning.__name__ in config:
            cfg = config[Types.SpatialBinning.__name__]
            extractor = SpatialBinner(color_space=cfg[Types.SpatialBinning.Space], size=cfg[Types.SpatialBinning.Size])
        elif Types.HOGExtractor.__name__ in config:
            cfg = config[Types.HOGExtractor.__name__]
            extractor = HogExtractor(orientations=cfg[Types.HOGExtractor.Orientations], hog_channel=cfg[Types.HOGExtractor.HogChannel], 
                size=cfg[Types.SpatialBinning.Size], 
                pixels_per_cell=cfg[Types.HOGExtractor.PixelsPerCell], 
                cells_per_block=cfg[Types.HOGExtractor.CellsPerBlock])
        else:
            raise ("Unrecognized extractor provided")
        extractors.append(extractor)
    
    return FeatureCombiner(tuple(extractors))