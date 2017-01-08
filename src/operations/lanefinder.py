'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
import numpy as np
from _collections import deque
import cv2
from operations.perspectivetransformer import PerspectiveTransformer

# Constants:
# Define conversions in x and y from pixels space to meters
ym_per_pix = 30/720 # meters per pixel in y dimension
xm_per_pix = 3.7/700 # meteres per pixel in x dimension
    
class Lane(object):
    def __init__(self, maxsize, yvals):
        self.maxsize = maxsize
        self.yvals = yvals
        self.xs = deque(maxlen=maxsize)
        self.fit = deque(maxlen=maxsize)
        self.fitxs = deque(maxlen=maxsize)
        self.curverad_ps = deque(maxlen=maxsize)
        self.curverad_rs = deque(maxlen=maxsize)
        self.confidences = deque(maxlen=maxsize)

    def add(self, xs, fit, fitx, curverad_ps, curverad_rs, confidence):
        assert confidence is not None or not (0 <= confidence <= 1.0), "Confidence value must always be between 0 and 1"
        self.xs.append(xs)
        self.fit.append(fit)
        self.fitxs.append(fitx)
        self.curverad_ps.append(curverad_ps)
        self.curverad_rs.append(curverad_rs)
        self.confidences.append(confidence)

    def get_relativeconfidence(self):
        if len(self.confidences) > 0:
            return self.confidences[-1]
        return None
        
    def get_totalconfidence(self):
        # This is relative to the scenario where all 'maxlen' points are known
        p = sum(self.confidences)
        pnorm = p / self.maxsize
            
        return pnorm
    
    def get_curverad(self):
        if len(self.curverad_ps) > 0:
            return self.curverad_ps[-1], self.curverad_rs[-1]
        return None, None
        
    def getyvals(self):
        return self.yvals
    
    def getlatestx(self):
        if len(self.xs) > 0:
            return self.xs[-1][0]
        return None

    def getlatestfitxs(self):
        if len(self.fitxs) > 0:
            if not self.fitxs[-1] is None:
                return list(self.fitxs[-1])
        return None

    def getlatestfitx(self, y):
        if len(self.fitxs) > 0:
            if not self.fitxs[-1] is None and len(self.fitxs[-1]) > 0:
                return int(self.fitxs[-1][self.yvals.index(y)])
        return None

    def getxhistory(self):
        return list(self.xs) # [item for sublist in self.xs for item in sublist]
        
class Car(object):
    def __init__(self, cameracenter_ps, cameracenter_rs):
        self.__position__ = None #Distance from center. Left of center = -, right of center = +
        self.__lanecenter_ps__ = None
        self.__lanecenter_rs__ = None
        self.__cameracenter_ps__ = cameracenter_ps
        self.__cameracenter_rs__ = cameracenter_rs

    def set_lanecenter(self, lanecenter_ps, lanecenter_rs):
        self.__lanecenter_ps__ = lanecenter_ps
        self.__lanecenter_rs__ = lanecenter_rs
        
    def get_lanecenter(self):
        return self.__lanecenter_ps__, self.__lanecenter_rs__

    def get_cameracenter(self):
        return self.__cameracenter_ps__, self.__cameracenter_rs__

#     def get_cameracenter(self):
#         return self.__cameracenter__
        
    def get_drift(self):
        if not self.__lanecenter_ps__ is None:
            return self.__cameracenter_ps__ - self.__lanecenter_ps__, self.__cameracenter_rs__ - self.__lanecenter_rs__
        return None, None
    
class PeakInfo(object):
    def __init__(self, peakrange, windowsize, timewindowctr, trackwindowctr, peak, value):
        self.windowsize = windowsize
        self.timewindowctr = timewindowctr
        self.trackwindowctr = trackwindowctr
        self.peakrange = peakrange
        self.peak = peak
        self.value = value

    def found(self):
        return self.peak is not None

# Detects the points on each lane and fits each with a polynomial function
# Also detects the position of the car relative to the center of the lane,
# based on the lane positions.
class LaneFinder(Operation):
    # Config:
    SliceRatio = 'SliceRatio'
    PeakWindowRatio = 'PeakWindowRatio'
    PeakRangeRatios = 'PeakRangeRatios'
    LookBackFrames = 'LookBackFrames'
    CameraPositionRatio = 'CameraPositionRatio'

    # Constants:
    CurrentPointRadius = 30
    CurrentPointColor = [255,0,0] #[50,205,50]
    PreviousPointRadius = 2
    PreviousPointColor = [0,0,0] #[152,251,152]
    HitWindowColor = [152, 251, 152]
    MissWindowColor = [255,160,122]
    SliceMarkerColor = [139,139,131]
    SliceMarkerThickness = 5
    VerticalCenterColor = [255,255,224]
    VerticalCenterThickness = 5
    
    # Outputs
    LeftLane = "LeftLane"
    RightLane = "RightLane"
    Car = 'Car'
    
    def __init__(self, params):
        Operation.__init__(self, params)
        self.__slice_ratio__ = params[self.SliceRatio]
        self.__peak_window_ratio__ = params[self.PeakWindowRatio]
        self.__peak_range_ratios__ = params[self.PeakRangeRatios]
        self.__look_back_frames__ = params[self.LookBackFrames]
        self.__camera_position_ratio__ = params[self.CameraPositionRatio]
        self.__left_lane__ = None
        self.__right_lane__ = None

    def __processupstream__(self, original, latest, data, frame):
        x_dim, y_dim = latest.shape[1], latest.shape[0]
        midx = int (x_dim / 2)
        if self.__left_lane__ is None:
            self.__slice_len__ = int(y_dim * self.__slice_ratio__)
            self.__peak_range__ = (int(self.__peak_range_ratios__[0] * self.__slice_len__), int(self.__peak_range_ratios__[1] * self.__slice_len__))
            self.__peak_window_size__ = int(x_dim * self.__peak_window_ratio__)
            self.__slices__ = []
            self.__yvals__ = []
            for idx in range (y_dim, 0, -self.__slice_len__):
                self.__slices__.append((idx, max(idx-self.__slice_len__, 0)))
                self.__yvals__.append(idx)
            if not 0 in self.__yvals__:
                self.__yvals__.append(0)
            self.__left_lane__ = Lane(self.__look_back_frames__, self.__yvals__)
            self.__right_lane__ = Lane(self.__look_back_frames__, self.__yvals__)
            self.__camera_position_ps__ = int(x_dim * self.__camera_position_ratio__)
            self.__camera_position_rs__ = int(x_dim * self.__camera_position_ratio__ * xm_per_pix)
            self.__car__ = Car(self.__camera_position_ps__, self.__camera_position_rs__)
            self.setdata(data, self.LeftLane, self.__left_lane__)
            self.setdata(data, self.RightLane, self.__right_lane__)
            self.setdata(data, self.Car, self.__car__)
                
        leftxs, rightxs, leftconfidence, rightconfidence, leftinfos, rightinfos = self.locate_peaks(latest, self.__slices__, self.__left_lane__, self.__right_lane__, self.__peak_window_size__, self.__peak_range__)
        
        # Prepare an illustration of the points:
#         if self.isplotting():
#             zeros1d = np.zeros_like(latest).astype(np.uint8)
#             foreground = np.dstack((zeros1d, zeros1d, zeros1d))
            
            # Things to plot:
            # - History of X values with size proportional to confidence level
            # - Last frame's fitted x
            # - This frame's X values
            # - Windows used to limit peak search
            # - Lines for the slices

        # Get previous points
        all_leftx = self.__left_lane__.getxhistory()
        all_rightx = self.__right_lane__.getxhistory()
        
        # Plot illustration of peak search:
        if self.isplotting():
            black1d = np.zeros_like(latest, dtype=np.uint8)
            foreground = np.dstack((black1d, black1d, black1d))
            background = self.getdata(data, PerspectiveTransformer.WarpedColor, PerspectiveTransformer).copy()
            
#             self.__plot__(frame, background, None, "Background", None)
            
            # Draw the vertical center:
            verticalcenter = np.copy(foreground)
            cv2.line(verticalcenter, (midx, y_dim), (midx, 0), self.VerticalCenterColor, self.VerticalCenterThickness)
#             self.__plot__(frame, verticalcenter, None, "VerticalCenter", None)
            
            # Draw the slices:
            slices = np.copy(foreground)
            for cut in self.__slices__:
                cv2.line(slices, (0, cut[0]), (x_dim, cut[0]), self.SliceMarkerColor, self.SliceMarkerThickness)
#             self.__plot__(frame, slices, None, "Slices", None)
            
            # Draw all the previous points found:
            previouspoints = np.copy(foreground)
            for j in range (len (all_leftx)):
                for i in range (len (self.__slices__)):
                    y = self.__slices__[i][0]
                    leftx = all_leftx[j][i]
                    rightx = all_rightx[j][i]
                    if leftx is not None:
                        cv2.circle(previouspoints, (leftx, y), self.PreviousPointRadius, self.PreviousPointColor, -1)
                    if rightx is not None:
                        cv2.circle(previouspoints, (rightx, y), self.PreviousPointRadius, self.PreviousPointColor, -1)
#             self.__plot__(frame, previouspoints, None, "PreviousPoints", None)
                
            # Draw the windows:
            timewindows = np.copy(foreground)
            for i in range (len (self.__slices__)):
                leftinfo, rightinfo = leftinfos[i], rightinfos[i]
                cut = self.__slices__[i]
                if leftinfo.timewindowctr is not None:
                    start = (max(leftinfo.timewindowctr-leftinfo.windowsize, 0), cut[0])
                    end = (min(leftinfo.timewindowctr+leftinfo.windowsize, midx), cut[1])
                    if leftinfo.found():
                        cv2.rectangle(timewindows, start, end, self.HitWindowColor, cv2.FILLED)
                    else:
                        cv2.rectangle(timewindows, start, end, self.MissWindowColor, cv2.FILLED)
                if rightinfo.timewindowctr is not None:
                    start = (max(rightinfo.timewindowctr-rightinfo.windowsize, midx), cut[0])
                    end = (min(rightinfo.timewindowctr+rightinfo.windowsize, x_dim), cut[1])
                    if rightinfo.found():
                        cv2.rectangle(timewindows, start, end, self.HitWindowColor, cv2.FILLED)
                    else:
                        cv2.rectangle(timewindows, start, end, self.MissWindowColor, cv2.FILLED)
#             self.__plot__(frame, timewindows, None, "Time Windows", None)
            
            trackwindows = np.copy(foreground)
            for i in range (len (self.__slices__)):
                leftinfo, rightinfo = leftinfos[i], rightinfos[i]
                cut = self.__slices__[i]
                if leftinfo.trackwindowctr is not None:
                    start = (max(leftinfo.trackwindowctr-leftinfo.windowsize, 0), cut[0])
                    end = (min(leftinfo.trackwindowctr+leftinfo.windowsize, midx), cut[1])
                    if leftinfo.found():
                        cv2.rectangle(trackwindows, start, end, self.HitWindowColor, cv2.FILLED)
                    else:
                        cv2.rectangle(trackwindows, start, end, self.MissWindowColor, cv2.FILLED)
                if rightinfo.trackwindowctr is not None:
                    start = (max(rightinfo.trackwindowctr-rightinfo.windowsize, midx), cut[0])
                    end = (min(rightinfo.trackwindowctr+rightinfo.windowsize, x_dim), cut[1])
                    if rightinfo.found():
                        cv2.rectangle(trackwindows, start, end, self.HitWindowColor, cv2.FILLED)
                    else:
                        cv2.rectangle(trackwindows, start, end, self.MissWindowColor, cv2.FILLED)
#             self.__plot__(frame, trackwindows, None, "Track Windows", None)
                        
            # Draw the found points
            foundpoints = np.copy(foreground)
            for i in range (len (self.__slices__)):
                leftinfo, rightinfo = leftinfos[i], rightinfos[i]
                cut = self.__slices__[i]
                if leftinfo.found():
                    cv2.circle(foundpoints, (leftinfo.peak, cut[0]-leftinfo.value), self.CurrentPointRadius, self.CurrentPointColor, -1)
                if rightinfo.found():
                    cv2.circle(foundpoints, (rightinfo.peak, cut[0]-rightinfo.value), self.CurrentPointRadius, self.CurrentPointColor, -1)
#             self.__plot__(frame, foundpoints, None, "FoundPoints", None)

            # Add all layers to the bw lane image:
            background = cv2.addWeighted(background, 1, verticalcenter, 0.3, 0)
            background = cv2.addWeighted(background, 1, slices, 0.3, 0)
            background = cv2.addWeighted(background, 1, previouspoints, 0.5, 0)
            background = cv2.addWeighted(background, 1, trackwindows, 0.3, 0)
            background = cv2.addWeighted(background, 1, timewindows, 0.3, 0)
            background = cv2.addWeighted(background, 1, foundpoints, 0.7, 0)
            
            self.__plot__(frame, background, None, "Peak Search Algorithm", None)

        # Combine historical points with present before doing a fit:
        all_leftx.append(leftxs)
        all_rightx.append(rightxs)
        all_leftys, all_leftxs = self.merge_prune(self.__yvals__, all_leftx)
        all_rightys, all_rightxs = self.merge_prune(self.__yvals__, all_rightx)
        
        # Find radius of curvature:
        left_fit, left_fitx, right_fit, right_fitx, left_curverad_ps, right_curverad_ps, left_curverad_rs, right_curverad_rs = None, None, None, None, None, None, None, None
        if len(all_leftys) > 0:
            # Fit a second order polynomial to each lane line
            left_fit, left_fitx = self.fit_polynomial(all_leftys, all_leftxs, np.array(self.__yvals__))
            y_left_eval = np.max(all_leftys)
            # Determine the curvature in pixel-space
            left_curverad_ps = ((1 + (2*left_fit[0]*y_left_eval + left_fit[1])**2)**1.5) \
                                 /np.absolute(2*left_fit[0])
            # Determine curvature in real space
            left_fit_cr = np.polyfit(all_leftys*ym_per_pix, all_leftxs*xm_per_pix, 2)
            left_curverad_rs = ((1 + (2*left_fit_cr[0]*y_left_eval + left_fit_cr[1])**2)**1.5) \
                                         /np.absolute(2*left_fit_cr[0])

        if len(all_rightys)>0:                                         
            # Fit a second order polynomial to each lane line
            right_fit, right_fitx = self.fit_polynomial(all_rightys, all_rightxs, np.array(self.__yvals__))
            y_right_eval = np.max(all_rightys)
    
            right_curverad_ps = ((1 + (2*right_fit[0]*y_right_eval + right_fit[1])**2)**1.5) \
                                            /np.absolute(2*right_fit[0])
    
            right_fit_cr = np.polyfit(all_rightys*ym_per_pix, all_rightxs*xm_per_pix, 2)
            right_curverad_rs = ((1 + (2*right_fit_cr[0]*y_right_eval + right_fit_cr[1])**2)**1.5) \
                                            /np.absolute(2*right_fit_cr[0])

        # Save values:
        self.__left_lane__.add(leftxs, left_fit, left_fitx, left_curverad_ps, left_curverad_rs, leftconfidence)
        self.__right_lane__.add(rightxs, right_fit, right_fitx, right_curverad_ps, right_curverad_rs, rightconfidence)
        lpos = self.__left_lane__.getlatestfitx(y_dim)
        rpos = self.__right_lane__.getlatestfitx(y_dim)
        if not lpos is None and not rpos is None:
            lanecenter_ps = (lpos + rpos) / 2
            lanecenter_rs = lanecenter_ps * xm_per_pix
            self.__car__.set_lanecenter(lanecenter_ps, lanecenter_rs)
            
        return latest
    
    def merge_prune(self, ys, xss):
        _yss = deque()
        _xss = deque()
        for xs in xss:
            _ys, _xs = self.prune_nulls(ys, xs)
            _yss.extend(_ys)
            _xss.extend(_xs)
            
        return np.array(_yss), np.array(_xss)
    
    def prune_nulls(self, ys, xs):
        _ys = []
        _xs = []
        for (y,x) in zip (ys, xs):
            if not x is None:
                _ys.append(y)
                _xs.append(x)
                
        return _ys, _xs

        
    def locate_peaks(self, latest, slices, leftlane, rightlane, windowsize, peakrange):
        leftxs = []
        rightxs = []
        leftinfos = []
        rightinfos = []
#         leftx, rightx = None, None
        leftxinfo, rightxinfo = None, None
        n_left_absent = 0
        n_right_absent = 0
        for yrange in slices:
            # The leftx and rightx points from the lower slice will be used to limit the search area
            # for discovering new peaks. If they were not found, the fitted x-values from the previous
            # frame's *next* slice will be used to limit the search area.
#             leftx = leftx if not leftx is None else leftlane.getlatestfitx(yrange[1])
#             rightx = rightx if not rightx is None else rightlane.getlatestfitx(yrange[1])
            leftxbelow = leftxinfo.peak if leftxinfo is not None else None
            rightxbelow = rightxinfo.peak if rightxinfo is not None else None
            
            # Look for the new points
            leftxinfo, rightxinfo = self.locate_peaks_in_slice(latest, yrange, leftlane, rightlane, leftxbelow, rightxbelow, windowsize, peakrange)
            if not leftxinfo.found():
                n_left_absent += 1
            if not rightxinfo.found():
                n_right_absent += 1
#             print ("Peaks in slice {} => {} ..... {} ".format(yrange, leftx, rightx))

            # Save the peaks -- they're precious
            leftxs.append(leftxinfo.peak)
            rightxs.append(rightxinfo.peak)
            leftinfos.append(leftxinfo)
            rightinfos.append(rightxinfo)

        leftconfidence = (len(slices) - n_left_absent) / len(slices)
        rightconfidence = (len(slices) - n_right_absent) / len(slices)
#         print ("Confidence: {0:.2f}, {1:.2f}".format(leftconfidence, rightconfidence))

        return leftxs, rightxs, leftconfidence, rightconfidence, leftinfos, rightinfos

    def locate_peaks_in_slice(self, latest, yrange, leftlane, rightlane, leftxbelow, rightxbelow, windowsize, peakrange):
        (y1, y2) = yrange
        midx = int(latest.shape[1] / 2)
        y_slice = latest[y1:y2:-1, : ]
        histogram = np.sum(y_slice, axis=0)

        # Adjust the previous points so that each half of the histogram can be calculated independently:
        leftpeakbefore = midx - leftlane.getlatestfitx(y1) if not leftlane.getlatestfitx(y1) is None else None
        rightpeakbefore = rightlane.getlatestfitx(y1) - midx if not rightlane.getlatestfitx(y1) is None else None
        leftpeakbelow = int(midx - leftxbelow) if not leftxbelow is None else None
        rightpeakbelow = int(rightxbelow - midx) if not rightxbelow is None else None

        leftx, leftval = self.find_peak(histogram[midx:0:-1], leftpeakbefore, leftpeakbelow, windowsize, peakrange)
        rightx, rightval = self.find_peak(histogram[midx:], rightpeakbefore, rightpeakbelow, windowsize, peakrange)

        # Revert actual points based on split:
        leftx = midx - leftx if not leftx is None else None
        rightx = midx + rightx if not rightx is None else None
        
        # Create search result:
        leftpeakinfo = PeakInfo(peakrange, windowsize, leftlane.getlatestfitx(y1), leftxbelow, leftx, leftval)
        rightpeakinfo = PeakInfo(peakrange, windowsize, rightlane.getlatestfitx(y1), rightxbelow, rightx, rightval)
        
        return leftpeakinfo, rightpeakinfo

    def find_peak(self, histogram, peakbefore, peakbelow, windowsize, peakrange):
        timewindow = [0, len(histogram)]
        if not peakbefore is None:
            timewindow = [max(0, peakbefore-windowsize), min(peakbefore+windowsize, len(histogram))]
        motionwindow = [0, len(histogram)]
        if not peakbelow is None:
            motionwindow = [max(0, peakbelow-windowsize), min(peakbelow+windowsize, len(histogram))]
        window = range(max(timewindow[0], motionwindow[0]), min(timewindow[1], motionwindow[1]))
#         window = range(min(timewindow[0], motionwindow[0]), max(timewindow[1], motionwindow[1])) # This might be too lenient

        # Iterate from left to right, looking for a peak that lies within a given range
        (low, high) = peakrange
        peak = None
        for i in window:
            assert i < len(histogram), "Info: TimeWindow {}, MotionWindow {}, Window {}, PeakRange {}, i {}".format(timewindow, motionwindow, window, peakrange, i)
            if histogram[i] >= high:
                peak = i    # Found!
                break
            elif low <= histogram[i] <= high:
                if peak is None:
                    peak = i
                else:
                    peak = i if histogram[i] > histogram[peak] else peak # Look for max
            else: # histogram[i] < low:
                continue    # Discard
                    
        return peak, int(histogram[peak]) if peak is not None else None
    
    def fit_polynomial(self, ys, xs, ystofit):
        assert len(ys) == len(xs), "Xs {} and Ys {} were not the same length.".format(len(xs), len(ys))
        fit, fitx = None, None
        if len(ys) > 0:
            fit = np.polyfit(ys, xs, 2)
            fitx = fit[0] * ystofit ** 2 + fit[1] * ystofit + fit[2]
        return fit, fitx

    def __processdownstream__(self, original, latest, data, frame):
        return latest
