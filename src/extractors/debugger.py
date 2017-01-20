'''
Created on Jan 19, 2017

@author: safdar
'''
import matplotlib
from utils.utilities import getallpathsunder
matplotlib.use('TKAgg')
from matplotlib.pyplot import get_current_fig_manager
from utils.plotter import Illustrator, Image, Graph
import cv2
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
import argparse
import json
from operations.vehiclefinder import VehicleFinder
from extractors.helper import getextractors
from extractors.hogextractor import HogExtractor
from extractors.spatialbinner import SpatialBinner
from extractors.colorhistogram import ColorHistogram

if __name__ == '__main__':
    print ("###############################################")
    print ("#          VEHICLE FEATURE EXPLORER           #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Object Classifier')
    parser.add_argument('-v', dest='vehicledir',    required=True, type=str, help='Path to folder containing vehicle images.')
    parser.add_argument('-n', dest='nonvehicledir',    required=True, type=str, help='Path to folder containing non-vehicle images.')
    parser.add_argument('-c', dest='configfile',    required=True, type=str, help='Path to configuration file (.json).')
    args = parser.parse_args()
    
    # Collect the image file names:
    print ("Gathering data...")
    cars = getallpathsunder(args.vehicledir)
    print ("Number of car images found: \t{}".format(len(cars)))
    assert len(cars)>0, "There should be at least one vehicle image to process. Found 0."
    notcars = getallpathsunder(args.nonvehicledir)
    print ("Number of non-car images found: \t{}".format(len(notcars)))
    assert len(notcars)>0, "There should be at least one non-vehicle image to process. Found 0."
    count = min(len(cars), len(notcars))
    zipped = zip(cars[:count], notcars[:count])
    
    print ("Loading extractors...")
    config = json.load(open(args.configfile))
    extractorsequence = config[VehicleFinder.__name__][VehicleFinder.FeatureExtractors]
    extractors = getextractors(extractorsequence)
    
    print ("Performing extraction...")
    illustrator = Illustrator(True)
    for (carfile, notcarfile) in zipped:
        car = mpimg.imread(carfile)
        notcar = mpimg.imread(notcarfile)
        frame = illustrator.nextframe()
        frame.newsection("Car")
        frame.newsection("Not-Car")
        frame.add(Image("Car", car, None), index=0)
        frame.add(Image("Not-Car", notcar, None), index=1)
        for (extractor,config) in zip(extractors, extractorsequence):
            if type(extractor) is HogExtractor:
                car_features, car_hogimage = extractor.extract(car, visualize=True)
                frame.add(Image("{}".format(config), car_hogimage, None), index=0)
                notcar_features, notcar_hogimage = extractor.extract(notcar, visualize=True)
                frame.add(Image("{}".format(config), notcar_hogimage, None), index=1)
            elif type(extractor) is SpatialBinner or type(extractor) is ColorHistogram:
                car_features = extractor.extract(car)
                frame.add(Graph("{}".format(config), None, car_features, None, None), index=0)
                notcar_features = extractor.extract(notcar)
                frame.add(Graph("{}".format(config), None, notcar_features, None, None), index=1)
            else:
                raise "Debugger is not aware of the extractor type: {}".format(extractor)
        frame.render()

    wm = plt.get_current_fig_manager() 
    wm.window.attributes('-topmost', 1)
    wm.window.attributes('-topmost', 0)
    plt.pause(100)