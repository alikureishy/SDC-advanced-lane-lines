'''
Created on Dec 22, 2016

@author: safdar
'''
import cv2

class BaseStreamer(object):
    def __init__(self, input, output):
        self.__inputfile__=input
        self.__outputfile__=output
        
class ImageStreamer(BaseStreamer):
    def __init__(self, input, output):
        BaseStreamer.__init__(self, input, output)

    def iterator(self):
        pre_image = cv2.imread(self.__inputfile__)
        return [pre_image]

    def write (self, post_image):
        if not self.__outputfile__==None:
            cv2.imwrite(self.__outputfile__, post_image)

    def __exit__(self):
        pass
        
class VideoStreamer(BaseStreamer):
    def __init__(self, inputfile, outputfile):
        BaseStreamer.__init__(self, inputfile, outputfile)
        self.__reader__ = cv2.VideoCapture(self.__inputfile__)
        if not self.__reader__.isOpened():
            raise "Unable to open input video file: {}".format(self.__inputfile__)

        # http://docs.opencv.org/3.1.0/dd/d43/tutorial_py_video_display.html
        # http://www.fourcc.org/codecs.php
        #     cv2.VideoWriter_fourcc('M', 'J', 'E', 'G')
        # http://www.pyimagesearch.com/2016/02/22/writing-to-video-with-opencv/
        # http://stackoverflow.com/questions/12290023/opencv-2-4-in-python-video-processing
        self.__writer__ = cv2.VideoWriter(self.__outputfile__, \
                                       -1, \
                                       self.__reader__.get('CV_CAP_PROP_FPS'), \
                                       (self.__reader__.get('CV_CAP_PROP_FRAME_WIDTH'),self.__reader__.get('CV_CAP_PROP_FRAME_HEIGHT')))
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
        if not self.__outputfile__==None:
            self.__writer__.write(post_image)
            self.__frameswritten__ += 1

    def __del__(self):
        self.__writer__.release()
        pass
