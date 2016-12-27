'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
from enum import Enum
import numpy as np    
import cv2

class Thresholder(Operation):
    Thresholds = 'Thresholds'
    ToPlotTerms = 'ToPlotTerms'
    class Term(Enum):
        def name(self):
            return self.__class__.__name__
    class Operator(Term):
        OR = 'OR'
        AND = 'AND'
        Operands = 'Operands'
    class SobelX(Term):
        Kernel = 'kernel'
        MinMax = 'threshold'
    class SobelY(Term):
        Kernel = 'kernel'
        MinMax = 'threshold'
    class SobelXY(Term):
        Kernel = 'kernel'
        MinMax = 'threshold'
    class SobelTanXY(Term):
        Kernel = 'kernel'
        MinMax = 'threshold'
    class Color(Term):
        Space = 'space'
        Channel = 'channel'
        MinMax = 'threshold'
        HLS = 'HLS'
        HSV = 'HSV'
        RGB = 'RGB'
        Gray = 'Gray'

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__sequence__ = self.getparam(self.Thresholds)
        self.__toplotterms__ = self.getparam(self.ToPlotTerms)
        self.__term__ = self.getparam(self.Term.name())

    def __processinternal__(self, original, latest, data, frame):
        term = self.getparam(self.Term.name())
        return self.__do_threshold__(latest, term, frame)
        
    def __do_threshold__(self, image, term, frame):
        assert type(term) is dict, "Every term must be a dictionary:\n{}".format(term)
        
        if self.Operator.name() in term:                    # Recursive case
            operator = term[self.Operator]
            operands = term[self.Operands]
            thresholded_binaries = []
            for term in operands:
                thresholded_binaries.append(self.__do_threshold__(image, term, frame))

            combined_binary = None
            if operator==self.Operator.OR:
                combined_binary = np.logical_or.reduce(thresholded_binaries)
            elif operator==self.Operator.AND:
                combined_binary = np.logical_and.reduce(thresholded_binaries)
            else:
                raise "Operator not supported: {}".format(operator)
            assert combined_binary.shape==thresholded_binaries[0].shape, \
                "Combined binary ({}) not the same shape as thresholded binaries ({})".format(combined_binary.shape, thresholded_binaries[0].shape)
            return combined_binary
        else:                                               # Base case
            assert len(term.keys())==1, "Term setting should have only one key, but has {}".format(len(term.keys()))
            flavor = term.keys()[0]
            binary_image = None
            if flavor==self.SobelX.name():
                binary_image = self.filter_sobel_x(image, 'x', term[flavor], frame)
            elif flavor==self.SobelY.name():
                binary_image = self.filter_sobel_y(image, 'y', term[flavor], frame)
            elif flavor==self.SobelXY.name():
                binary_image = self.filter_sobel_xy(image, term[flavor], frame)
            elif flavor==self.SobelTanXY.name():
                binary_image = self.filter_sobel_tanxy(image, term[flavor], frame)
            elif flavor==self.Color.name():
                binary_image = self.filter_color(image, term[flavor], frame)
            else:
                raise "Threshold type not recognized: {}".format(flavor)

            title = "{}".format(term)
            stats = None
            self.__plot__(frame, binary_image, 'gray', title, stats)
            return binary_image

    def __makegray__(self, image):
        gray = None
        if ((len(image.shape) < 3) or (image.shape[2] < 3)):
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return gray

    def __binaryforrange__(self, minmax, image):
        binary_sobel = np.zeros_like(image)
        binary_sobel[(image >= minmax[0]) & (image <= minmax[1])] = 1
        return binary_sobel

    def __scaleimage__(self, image):
        image = np.absolute(image)
        if (np.max(image) > 255):
            image = np.uint8(255 * image / np.max(image))
        return image

    def __filter_sobel__(self, image, orientation, term, frame):
        kernel = term[self.SobelTanXY.Kernel]
        minmax = term[self.SobelTanXY.MinMax]
        gray = self.__makegray__(image)
        sobel = None
        assert orientation=='x' or orientation=='y', "Orientation should be either 'x' or 'y'. Got {}".format(orientation)
        if orientation=='x':
            sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel)
        else:
            sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel)
    
        abs_sobel = np.absolute(sobel)
        scaled_sobel = self.__scaleimage__(abs_sobel)
        binary_sobel = self.__binaryforrange__(minmax, scaled_sobel)
        return binary_sobel

    def filter_sobel_x(self, image, term, frame):
        return self.__filter_sobel__(image, 'x', term, frame)

    def filter_sobel_y(self, image, term, frame):
        return self.__filter_sobel__(image, 'y', term, frame)

    def filter_sobel_xy(self, image, term, frame):
        kernel = term[self.SobelTanXY.Kernel]
        minmax = term[self.SobelTanXY.MinMax]
        gray = self.__makegray__(image)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel)
        abs_sobel = np.sqrt(sobelx**2 + sobely**2)
        scaled_sobel = self.__scaleimage__(abs_sobel)
        binary_sobel = self.__binaryforrange__(minmax, scaled_sobel)
        return binary_sobel

    def filter_sobel_tanxy(self, image, term, frame):
        kernel = term[self.SobelTanXY.Kernel]
        minmax = term[self.SobelTanXY.MinMax]
        gray = self.__makegray__(image)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel)
        abs_sobelx = np.absolute(sobelx)
        abs_sobely = np.absolute(sobely)
        tan_sobel = np.arctan2(abs_sobely, abs_sobelx)
        binary_sobel = self.__binaryforrange__(minmax, tan_sobel)
        return binary_sobel
    
    def filter_color(self, image, term, frame):
        space = term[self.Color.Space]
        channel = term[self.Color.Channel]
        minmax = term[self.Color.MinMax]
    
        component = None
        if space == self.Color.HLS:
            if len(image.shape)<3 | image.shape[2]<3:
                raise "Image provided with shape {} cannot be used to extract target {}".format(image.shape, space)
            hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
            component = hls[:,:,channel]
        elif space == self.Color.HSV:
            if len(image.shape)<3 | image.shape[2]<3:
                raise "Image provided with shape {} cannot be used to extract target {}".format(image.shape, space)
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            component = hsv[:,:,channel]
        elif space == self.Color.RGB:
            if len(image.shape)<3 | image.shape[2]<3:
                raise "Image provided with shape {} cannot be used to extract target {}".format(image.shape, space)
            rgb = image # Since we should have converted to RGB earlier
            component = rgb[:,:,channel]
        elif space == self.Color.Gray:
            if len(image.shape)==3 & image.shape[2]==3:
                component = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                component = image
        else:
            raise "Unrecognized target space: {}".format(space)
        
        mask = self.__scaleimage__(component)
        binary = self.__binaryforrange__(minmax, mask)
        return binary
