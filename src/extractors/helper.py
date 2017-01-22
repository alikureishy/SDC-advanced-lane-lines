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
        Channel = 'Channel'
    class ColorHistogram(object):
        Space = 'Space'
        NumBins = 'NumBins'
        BinRange = 'BinRange'
        Channel = 'Channel'
    class HOGExtractor(object):
        Orientations = 'Orientations'
        Channel = 'Channel'
        PixelsPerCell = 'PixelsPerCell'
        CellsPerBlock = 'CellsPerBlock'
        Size = 'Size'
    
    
def getextractors(extractorsequence):
    extractors = []
    for config in extractorsequence:
        assert len(config.keys()) == 1, "Invalid: {}".format(config)
        extractor = None
        if Types.ColorHistogram.__name__ in config:
            cfg = config[Types.ColorHistogram.__name__]
            extractor = ColorHistogram(color_space=cfg[Types.ColorHistogram.Space], nbins=cfg[Types.ColorHistogram.NumBins], 
                                       bins_range=cfg[Types.ColorHistogram.BinRange], channel=cfg[Types.ColorHistogram.Channel])
        elif Types.SpatialBinning.__name__ in config:
            cfg = config[Types.SpatialBinning.__name__]
            extractor = SpatialBinner(color_space=cfg[Types.SpatialBinning.Space], size=cfg[Types.SpatialBinning.Size],
                                      channel=cfg[Types.SpatialBinning.Channel])
        elif Types.HOGExtractor.__name__ in config:
            cfg = config[Types.HOGExtractor.__name__]
            extractor = HogExtractor(orientations=cfg[Types.HOGExtractor.Orientations], channel=cfg[Types.HOGExtractor.Channel], 
                                     size=cfg[Types.SpatialBinning.Size], 
                                     pixels_per_cell=cfg[Types.HOGExtractor.PixelsPerCell], 
                                     cells_per_block=cfg[Types.HOGExtractor.CellsPerBlock])
        else:
            raise ("Unrecognized extractor provided")
        extractors.append(extractor)
        
    return extractors
    
def buildextractor(extractorsequence):
    extractors = getextractors(extractorsequence)
    return FeatureCombiner(tuple(extractors))

def buildclassifier(classifierconfig):
    pass