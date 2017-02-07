'''
Created on Dec 21, 2016

@author: safdar
'''
import matplotlib
matplotlib.use('TKAgg')
from sklearn.neural_network.multilayer_perceptron import MLPClassifier
from skimage.io import imread
from sklearn.cross_validation import train_test_split
from sklearn.svm.classes import LinearSVC, SVC
import time
import json
from operations.vehicledetection.vehiclefinder import VehicleFinder
from extractors.helper import buildextractor
import argparse
import numpy as np
import os
from sklearn.externals import joblib

CAR_FLAG = 1
NOTCAR_FLAG = 0

def getallpathsunder(path):
    if not os.path.isdir(path):
        raise "Folder {} does not exist, or is not a folder".format(path)
    cars = [os.path.join(dirpath, f)
            for dirpath, _, files in os.walk(path)
            for f in files if f.endswith('.png')]
    return cars

def appendXYs(imagefiles, extractor, label, Xs, Ys):
    print ("Extracting features for '{}'".format("Cars" if label == 1 else "Non-Cars"))
    for idx, file in enumerate(imagefiles):
        image = imread(file) # Change to skimage.io.imread() to get pixel values within [0,255]
#         image = np.array(PIL.Image.open(file))
        featurevector = extractor.extract(image)
        Xs.append(featurevector)
        Ys.append(label)
        if idx % 100 == 0:
            print(".", end='', flush=True)
    print("")

if __name__ == '__main__':
    print ("###############################################")
    print ("#          VEHICLE DETECTION TRAINER          #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Object Classifier')
    parser.add_argument('-v', dest='vehicledir',    required=True, type=str, help='Path to folder containing vehicle images.')
    parser.add_argument('-n', dest='nonvehicledir',    required=True, type=str, help='Path to folder containing non-vehicle images.')
    parser.add_argument('-c', dest='configfile',    required=True, type=str, help='Path to configuration file (.json).')
    parser.add_argument('-f', dest='outputfile',   required=True, type=str, help='File to store trainer parameters for later use')
    parser.add_argument('-t', dest='testratio', default=0.10, type=float, help='% of training data held aside for testing.')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    parser.add_argument('-o', dest='overwrite', action='store_true', help='Will save over existing file on disk (default: false).')
    args = parser.parse_args()

    # Collect the image file names:
    print ("Gathering data...")
    cars = getallpathsunder(args.vehicledir)
    print ("Number of car images found: \t{}".format(len(cars)))
    assert len(cars)>0, "There should be at least one vehicle image to process. Found 0."
    notcars = getallpathsunder(args.nonvehicledir)
    print ("Number of non-car images found: \t{}".format(len(notcars)))
    assert len(notcars)>0, "There should be at least one non-vehicle image to process. Found 0."

    # Create all the extractors here:
    print ("Preparing feature extractors...")
    config = json.load(open(args.configfile))
    extractorsequence = config[VehicleFinder.__name__][VehicleFinder.FeatureExtractors]
    combiner = buildextractor(extractorsequence)

    # Prepare feature vectors:
    print ("Extracting features...")
    Xs, Ys = [], []
    appendXYs(cars, combiner, CAR_FLAG, Xs, Ys)
    appendXYs(notcars, combiner, NOTCAR_FLAG, Xs, Ys)
    Xs = np.array(Xs, dtype=np.float64)
    print ("\tFeatures shape: {}".format(Xs.shape))

    # Prepare data:
    # - Normalize, shuffle and split:
#     print ("Preparing data")
#     X_scaler = StandardScaler().fit(Xs)
#     scaled_Xs = X_scaler.transform(Xs)
#     scaled_Xs, Ys = shuffle(scaled_Xs, Ys, random_state=rand_state)
    rand_state = np.random.randint(0, 100)
    X_train, X_test, Y_train, Y_test = train_test_split(Xs, Ys, test_size=args.testratio, random_state=rand_state)

    # If the SVM was not already trained:
    classifier = None
    if args.overwrite is True or not os.path.isfile(args.outputfile):
        print ("Training the SVC...")
#         classifier = MLPClassifier()
        classifier = LinearSVC()
        t=time.time()
        classifier.fit(X_train, Y_train)
        t2 = time.time()
        print(t2-t, 'Seconds to train SVC...')
    else:
        args.dry = True
        print ("SVC already trained. Reading from previous version.")
        classifier = joblib.load(args.outputfile)

    print('Train Accuracy of SVC = ', classifier.score(X_train, Y_train))
    print('Test Accuracy of SVC = ', classifier.score(X_test, Y_test))
    t= time.time()
    prediction = classifier.predict(X_test[0].reshape(1, -1))
    t2 = time.time()
    print(t2-t, 'Seconds to predict with SVC')

    if not args.dry or args.overwrite is True:
        print ("Saving classifier to file: {}".format(args.outputfile))
        joblib.dump(classifier, args.outputfile)

    print ("Thank you. Come again!")
