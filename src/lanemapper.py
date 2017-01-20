'''
Created on Dec 21, 2016

@author: safdar
'''
import matplotlib
matplotlib.use('TkAgg')
import argparse
import os
from operations.pipeline import Pipeline
from utils.streamers import ImageStreamer, VideoStreamer
from utils.plotter import Illustrator
import json

if __name__ == '__main__':
    print ("###############################################")
    print ("#                 LANE FINDER                 #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Lane Finder')
    parser.add_argument('-i', dest='input',    required=True, type=str, help='Path to image file, image folder, or video file.')
    parser.add_argument('-o', dest='output',   type=str, help='Location of output (Will be treated as the same as input type)')
    parser.add_argument('-c', dest='configs',   required=True, nargs='*', type=str, help="Configuration files.")
    parser.add_argument('-s', dest='selector', type=int, help='Short circuit the pipeline to perform only specified # of operations.')
    parser.add_argument('-x', dest='speed', type=int, default=1, help='Speed (1 ,2, 3 etc) interpreted as 1x, 2x, 3x etc)')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    parser.add_argument('-p', dest='plot', action='store_true', help='Plot all illustrations marked as \'ToPlot\' in the config. (default: false).')
    args = parser.parse_args()

    # Create the pipelines
    pipelines = []
    illustrator = Illustrator(args.plot)
    for file in args.configs:
        config = json.load(open(file))
        pipeline = Pipeline(config, args.selector)
        pipelines.append((file, pipeline))

    if len(pipelines)>1:
        print ("More than 1 pipeline. Switching to dry mode.")
        args.output = None
        args.dry = True

    # Create the reader/writer
    streamer = None
    if os.path.isfile(args.input):
        if args.input.endswith('.jpg') | args.input.endswith('.JPG'):
            streamer = ImageStreamer(args.input, args.output, args.dry)
        elif args.input.endswith('.mp4') | args.input.endswith('.MP4'):
            streamer = VideoStreamer(args.input, args.output, args.dry)
        else:
            raise "Unrecognized input file type: {}".format(args.input)
    else:
        raise "Unrecognized input type: {}".format(args.input)

    # Process:
    framecount = 0
    for image in streamer.iterator():
        if framecount % args.speed == 0:
            frame = illustrator.nextframe()
            for (name, pipeline) in pipelines:
                frame.newsection(name)
                processed = pipeline.execute(image, frame)
                streamer.write(processed)
            frame.render()
        framecount+=1
    
#     cv2.waitKey()
    # End
    print ("\nThank you. Come again!")