'''
Created on Dec 21, 2016

@author: safdar
'''
import argparse
import os
from operations.pipeline import Pipeline
from utils.streamers import ImageStreamer, VideoStreamer
from utils.plotter import Plotter
import json

if __name__ == '__main__':
    print ("###############################################")
    print ("#                 LANE FINDER                 #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Lane Finder')
    parser.add_argument('-i', dest='input',    required=True, type=str, help='Path to image file, image folder, or video file.')
    parser.add_argument('-o', dest='output',   required=True, type=str, help='Location of output (Will be treated as the same as input type)')
    parser.add_argument('-c', dest='configs',   required=True, nargs='*', type=str, help="Configuration files.")
    parser.add_argument('-s', dest='selector', help='Short circuit the pipeline to perform only selected operation.')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    args = parser.parse_args()

    # Create the pipelines
    pipelines = []
    plotter = Plotter()
    for file in args.configs:
        config = json.load(open(file))
        pipeline = Pipeline(config, args.selector)
        plotter.register(pipeline)
        pipelines.add()

    # Create the reader/writer
    streamer = None
    if os.path.isfile(args.input):
        if args.input.endswith('.jpg') | args.input.endswith('.JPG'):
            streamer = ImageStreamer(args.input, args.output)
        elif args.input.endswith('.mp4') | args.input.endswith('.MP4'):
            streamer = VideoStreamer(args.input, args.output)
        else:
            raise "Unrecognized input file type: {}".format(args.input)
    else:
        raise "Unrecognized input type: {}".format(args.input)

    # Process:
    with streamer:
        for image in streamer.iterator():
            plot = plotter.nextframe()
            for pipeline in pipelines:
                processed = pipeline.execute(image, plot)
                if not args.dry:
                    streamer.write(processed)
            plot.render()
    
    # End
    print ("Thank you. Come again!")