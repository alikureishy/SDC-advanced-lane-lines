'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np    
import cv2

class Thresholder(Operation):
    class Term(object):
        _ = 'Term'
        ToPlot = 'ToPlot'
        Negate = 'Negate'
    class Expr(Term):
        OR = 'OR'
        AND = 'AND'
        SEQ = "SEQ"
        Operands = 'Operands'
        Operator = 'Operator'
    class SobelX(Term):
        _ = 'SobelX'
        Kernel = 'Kernel'
        MinMax = 'MinMax'
    class SobelY(Term):
        _ = 'SobelY'
        Kernel = 'Kernel'
        MinMax = 'MinMax'
    class SobelXY(Term):
        _ = 'SobelXY'
        Kernel = 'Kernel'
        MinMax = 'MinMax'
    class SobelTanXY(Term):
        _ = 'SobelTanXY'
        Kernel = 'Kernel'
        MinMax = 'MinMax'
    class Canny(Term):
        _ = 'Canny'
        Blur = 'Blur'
        LowHigh = 'LowHigh'
#         Rho = 'Rho'
#         Theta = 'Theta'
#         Threshold = 'Threshold'
#         MinLen = 'MinLen'
#         MaxGap = 'MaxGap'
    class Color(Term):
        _ = 'Color'
        Space = 'Space'
        Channel = 'Channel'
        MinMax = 'MinMax'
        HLS = 'HLS'
        HSV = 'HSV'
        RGB = 'RGB'
        Gray = 'Gray'

    def __init__(self, params):
        Operation.__init__(self, params)
        self.__term__ = self.getparam(self.Term._)

    def __processupstream__(self, original, latest, data, frame):
        return self.__do_threshold__(latest, self.__term__, frame)
        
    def __do_threshold__(self, image, term, frame):
        assert type(term) is dict, "Every term must be a dictionary:\n{}".format(term)
        
        if self.Expr.Operator in term:                    # Recursive case
            operator = term[self.Expr.Operator]
            operands = term[self.Expr.Operands]
            toplot = term[self.Expr.ToPlot]
            negate = term[self.Term.Negate] if self.Term.Negate in term else 0

            if operator == self.Expr.SEQ:
                binary = None
                for term in operands:
                    binary = self.__do_threshold__(image, term, frame)
                    image = binary
                combined_binary = binary
            elif operator == self.Expr.AND or operator == self.Expr.OR:
                thresholded_binaries = []
                for term in operands:
                    thresholded_binaries.append(self.__do_threshold__(image, term, frame))
    
                combined_binary = None
                if operator==self.Expr.OR:
                    combined_binary = np.bitwise_or.reduce(thresholded_binaries)
                elif operator==self.Expr.AND:
                    combined_binary = np.bitwise_and.reduce(thresholded_binaries)
            else:
                raise "Operator not supported: {}".format(operator)

            combined_binary = combined_binary * 1
            stats = None
            title = ">>> {}".format(operator)
            self.__plot__(frame, combined_binary, 'gray', title, stats, toplot=toplot)
            
            if negate:
                combined_binary = cv2.bitwise_not(combined_binary)
                title = "{} >>> NOT".format(operator)
                self.__plot__(frame, combined_binary, 'gray', title, stats, toplot=toplot)

            return combined_binary
        else:                                               # Base case
            assert len(term.keys())==1, "Term setting should have only one key, but has {}".format(len(term.keys()))
            flavor = list(term.keys())[0]
            termconfig = term[flavor]
            toplot = termconfig[self.Term.ToPlot]
            negate = termconfig[self.Term.Negate] if self.Term.Negate in termconfig else 0
            
            binary_image = None
            if flavor==self.SobelX._:
                binary_image = self.filter_sobel_x(image, termconfig, frame)
            elif flavor==self.SobelY._:
                binary_image = self.filter_sobel_y(image, termconfig, frame)
            elif flavor==self.SobelXY._:
                binary_image = self.filter_sobel_xy(image, termconfig, frame)
            elif flavor==self.SobelTanXY._:
                binary_image = self.filter_sobel_tanxy(image, termconfig, frame)
            elif flavor==self.Canny._:
                binary_image = self.canny(image, termconfig, frame)
            elif flavor==self.Color._:
                binary_image = self.filter_color(image, termconfig, frame)
            else:
                raise "Threshold type not recognized: {}".format(flavor)

            stats = None
            title = "{}".format(term)
            self.__plot__(frame, binary_image, 'gray', title, stats, toplot=toplot)

            if negate:
                binary_image = cv2.bitwise_not(np.uint8(binary_image))
                title = "{} >>> NOT".format(flavor)
                self.__plot__(frame, binary_image, 'gray', title, stats, toplot=toplot)

            return binary_image

    #######################################################################
    
    def __makegray__(self, image):
        gray = None
        if ((len(image.shape) < 3) or (image.shape[2] < 3)):
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return gray

    def __binaryforrange__(self, minmax, image):
        binary_sobel = np.zeros_like(image)
        binary_sobel[(image > minmax[0]) & (image < minmax[1])] = 1
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
    
    def canny(self, image, term, frame):
        blur = term[self.Canny.Blur]
        lowhigh = term[self.Canny.LowHigh]
        gray = self.__makegray__(image)
        if blur>0:
            gray = cv2.GaussianBlur(gray, (blur, blur), 0)
        canny = cv2.Canny(gray, lowhigh[0], lowhigh[1])
        return canny
    
#     def hough_lines(self, image, term, frame):
#         lines = cv2.HoughLinesP(image, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    
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
