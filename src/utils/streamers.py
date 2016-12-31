'''
Created on Dec 22, 2016

@author: safdar
'''
import cv2

class BaseStreamer(object):
    def __init__(self, input, output, dry=False):
        self.__inputfile__=input
        self.__outputfile__=output
        self.__dry__ = dry
        
class ImageStreamer(BaseStreamer):
    def __init__(self, input, output, dry=False):
        BaseStreamer.__init__(self, input, output, dry)

    def iterator(self):
        pre_image = cv2.imread(self.__inputfile__)
        return [pre_image]

    def write (self, post_image):
        if not ((self.__outputfile__==None) | (self.__dry__==True)):
            cv2.imwrite(self.__outputfile__, post_image)

    def __exit__(self):
        pass
        
class VideoStreamer(BaseStreamer):
    def __init__(self, inputfile, outputfile, dry=False):
        BaseStreamer.__init__(self, inputfile, outputfile, dry)
        self.__reader__ = cv2.VideoCapture(self.__inputfile__)
        if not self.__reader__.isOpened():
            raise "Unable to open input video file: {}".format(self.__inputfile__)

        # http://docs.opencv.org/3.1.0/dd/d43/tutorial_py_video_display.html
        # http://www.fourcc.org/codecs.php
        #     cv2.VideoWriter_fourcc('M', 'J', 'E', 'G')
        # http://www.pyimagesearch.com/2016/02/22/writing-to-video-with-opencv/
        # http://stackoverflow.com/questions/12290023/opencv-2-4-in-python-video-processing
        fps = int(self.__reader__.get(cv2.CAP_PROP_FPS))
        width = int(self.__reader__.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.__reader__.get(cv2.CAP_PROP_FRAME_HEIGHT))
        count = int(self.__reader__.get(cv2.CAP_PROP_FRAME_COUNT))
        print ("{}:\n\tFPS = {}\n\tWidth, Height= ({}, {})\n\tFrame Count={}".format(inputfile, fps, width, height, count))
        
        self.__writer__ = None
        self.__writer__ = cv2.VideoWriter(self.__outputfile__, \
                                       cv2.VideoWriter_fourcc('m','p','4','v'), \
                                       fps, \
                                       (width,height))
        if not self.__writer__.isOpened():
            raise "Unable to open output video file: {}".format(self.__outputfile__)
        
        self.__framesread__ = 0
        self.__frameswritten__ = 0

    def iterator(self):
        while(self.__reader__.isOpened()):
            ret, image = self.__reader__.read()
            if not ret:
                break
            self.__framesread__ += 1
            yield image

    def write (self, post_image):
        if not ((self.__outputfile__==None) | (self.__dry__==True)):
            self.__writer__.write(post_image)
            self.__frameswritten__ += 1
            print ("\tWrote frame: {}". format(self.__frameswritten__))

    def __del__(self):
        if not self.__writer__ is None:
            self.__writer__.release()
