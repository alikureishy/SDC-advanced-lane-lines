'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np    
import cv2
from utils.utilities import drawlines, extractlanes
from utils.plotter import Image
from utils.plotter import Graph


# Supported operations
# - Color -> InRange -> 0/1
# - Color HSV/H -> Sobel -> InRange -> 0/1 -> Shift/Negate
# - Color HLS/S -> Sobel -> InRange -> 0/1
# - Color HLS/S -> InRange
# - Color -> OfRange ->

# Operators:
# - Multi-Channel / Continuous
#    -             (OPERATOR) VStack/HStack/DStack
#    - (Term) OfRange
#    - (Term) Roll
#    - (Term) Spread
# - Single-Channel / Continuous
#    - (Term) Sobel
#    - (Term) InRange
#    - (Term) Roll
# - Multi-Channel / Binary
#    - VStack/HStack/DStack
#    - InRange
#    - Roll
# - Single-Channel / Binary
#    - InRange
#    - (Term) Canny
#    - Roll

class Thresholder(Operation):
    Term_ = 'Term'
    HoughFilter = 'HoughFilter'
    class Term(object):
        ToPlot = 'ToPlot'
        Negate = 'Negate'
        Canny = 'Canny'
        Hough = 'Hough'
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
        self.__term__ = self.getparam(self.Term_)

    def __processupstream__(self, original, latest, data, frame):
        latest = np.uint8(latest)
        return self.__do_threshold__(latest, self.__term__, frame)
        
    def __do_threshold__(self, image, term, frame):
        assert type(term) is dict, "Every term must be a dictionary:\n{}".format(term)
        
        if self.Expr.Operator in term:                    # Recursive case
            operator = term[self.Expr.Operator]
            operands = term[self.Expr.Operands]
            toplot = term[self.Expr.ToPlot]
            negate = term[self.Term.Negate] if self.Term.Negate in term else 0
            canny = term[self.Term.Canny] if self.Term.Canny in term else None
            hough = self.getparam(self.HoughFilter) if term.get(self.Term.Hough, 0) == 1 else None

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

            stats = None
            
            title = ">> {}".format(operator)
            if negate:
                combined_binary = np.absolute(1 - combined_binary)
                title = "{} >> NOT".format(title)

            self.__plot__(frame, Image(title, combined_binary, 'gray'), toplot=toplot)

            if not canny is None:
                combined_binary = cv2.Canny(combined_binary, canny[0], canny[1])
                title = ">> CANNY ({})".format(canny)
                self.__plot__(frame, Image(title, combined_binary, 'gray'), toplot=toplot)

            if not hough is None:
                lines,left,right = extractlanes(combined_binary, hough)
                title = ">> HOUGH".format(hough)
                if left is None or right is None:
                    hough_image = drawlines(np.zeros_like(combined_binary), lines)
                else:
                    hough_image = drawlines(np.zeros_like(combined_binary), [left,right])
                self.__plot__(frame, Image(title, hough_image, 'gray'), toplot=toplot)
                
            return combined_binary
        else:                                               # Base case
            assert len(term.keys())==1, "Term setting should have only one key, but has {}".format(len(term.keys()))
            flavor = list(term.keys())[0]
            termconfig = term[flavor]
            toplot = termconfig[self.Term.ToPlot]
            negate = termconfig[self.Term.Negate] if self.Term.Negate in termconfig else 0
            canny = termconfig[self.Term.Canny] if self.Term.Canny in termconfig else None
            hough = self.getparam(self.HoughFilter) if termconfig.get(self.Term.Hough, 0) == 1 else None
            
            binary_image = None
            if flavor==self.SobelX._:
                binary_image = self.filter_sobel_x(image, termconfig, frame)
            elif flavor==self.SobelY._:
                binary_image = self.filter_sobel_y(image, termconfig, frame)
            elif flavor==self.SobelXY._:
                binary_image = self.filter_sobel_xy(image, termconfig, frame)
            elif flavor==self.SobelTanXY._:
                binary_image = self.filter_sobel_tanxy(image, termconfig, frame)
            elif flavor==self.Color._:
                binary_image = self.filter_color(image, termconfig, frame)
            else:
                raise "Threshold type not recognized: {}".format(flavor)

            stats = None
            title = "{}-{}".format(flavor, self.removekeys(termconfig, [self.Term.ToPlot, self.Term.Negate, self.Term.Canny, self.Term.Hough]))
            
            if negate:
                binary_image = np.absolute(1 - binary_image)
                title = "NOT ({})".format(title)
            
            self.__plot__(frame, Image(title, binary_image, 'gray'), toplot=toplot)
            
            if not canny is None:
                binary_image = cv2.Canny(binary_image, canny[0], canny[1])
                title = "{} >> CANNY ({})".format(flavor, canny)
                self.__plot__(frame, Image(title, binary_image, 'gray'), toplot=toplot)

            if not hough is None:
                lines,left,right = extractlanes(binary_image, hough)
                title = "{} >> HOUGH".format(flavor)
                if left is None or right is None:
                    hough_image = drawlines(np.zeros_like(binary_image), lines)
                else:
                    hough_image = drawlines(np.zeros_like(binary_image), [left,right])
                self.__plot__(frame, Image(title, hough_image, 'gray'), toplot=toplot)

            return binary_image

    #######################################################################
    
    def removekeys(self, d, keys):
        return {key: d[key] for key in d if key not in keys}
    
    def __makegray__(self, image):
        gray = None
        if ((len(image.shape) < 3) or (image.shape[2] < 3)):
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return gray

    def __binaryforrange__(self, minmax, image):
        binary_sobel = np.zeros_like(image, dtype=np.uint8)
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
