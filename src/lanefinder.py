'''
Created on Dec 21, 2016

@author: safdar
'''
import argparse
import configparser
import os
from chain import Chain
from streamers import ImageStreamer, VideoStreamer
from plotter import Plotter

if __name__ == '__main__':
    print ("###############################################")
    print ("#                 LANE FINDER                 #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Lane Finder')
    parser.add_argument('-i', dest='input',    required=True, type=str, help='Path to image file, image folder, or video file.')
    parser.add_argument('-f', dest='output',   required=True, type=str, help='Location of output (Will be treated as the same as input type)')
    parser.add_argument('-c', dest='config',   required=True, nargs='*', type=str, help="Configuration files.")
    parser.add_argument('-o', dest='overwrite', action='store_true', help='Overwrite output file(s) if they already exist (default: false)')
    parser.add_argument('-r', dest='realtime', action='store_true', help='Display real time image of advanced lane detection. (default: false)')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    parser.add_argument('-s', dest='stats', action='store_true', help='Will print statistics to the output display and file (default: false).')
    args = parser.parse_args()

    # Create the chains
    chains = []
    plotter = Plotter(realtime=args.realtime)
    for file in args.configs:
        config = configparser.ConfigParser()
        config.read(file)
        chain = Chain(config)
        plotter.register(chain)
        chains.add()

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
            for chain in chains:
                processed = chain.execute(image, plot)
                if not args.dry:
                    streamer.write(processed)
            plot.render()
    
    # End
    print ("Thank you. Come again!")