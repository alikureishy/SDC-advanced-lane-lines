'''
Created on Dec 23, 2016

@author: safdar
'''
from operations.baseoperation import Operation
from operations.lanefinder import LaneFinder
import cv2
    
# Writes statistics to the output image    
class StatsWriter(Operation):
    OrigXRatio = 0.20
    OrigYRatio = 0.98
    Font = cv2.FONT_HERSHEY_COMPLEX
    FontScale = 0.10
    CaptionColor = (255, 255, 255)
    CaptionThickness = 2
    
    def __init__(self, params):
        Operation.__init__(self, params)

    # Processed downstream since by now all the info would be available
    def __processdownstream__(self, original, latest, data, frame):
        leftlane = self.getdata(data, LaneFinder.LeftLane, LaneFinder)
        rightlane = self.getdata(data, LaneFinder.RightLane, LaneFinder)
        car = self.getdata(data, LaneFinder.Car, LaneFinder)
        if not leftlane is None and not rightlane is None and not car is None:
            x, y = int(latest.shape[1]*self.OrigXRatio), int(latest.shape[0]*self.OrigYRatio)
            leftcurverad_ps, leftcurverad_rs = leftlane.get_curverad()
            rightcurverad_ps, rightcurverad_rs = rightlane.get_curverad()
            drift_ps, drift_rs = car.get_drift()
            leftconfidence, rightconfidence = leftlane.get_totalconfidence()*100.0, rightlane.get_totalconfidence()*100.0
#             cameracenter_ps, cameracenter_rs = car.get_cameracenter()
            leftcurverad_ps = "~~~~" if leftcurverad_ps is None else '{0:.2f}'.format(leftcurverad_ps)
            rightcurverad_ps = "~~~~" if rightcurverad_ps is None else '{0:.2f}'.format(rightcurverad_ps)
            leftcurverad_rs = "~~~~" if leftcurverad_rs is None else '{0:.2f}'.format(leftcurverad_rs)
            rightcurverad_rs = "~~~~" if rightcurverad_rs is None else '{0:.2f}'.format(rightcurverad_rs)
            drift_ps = "~~~~" if drift_ps is None else '{0:.2f}'.format(drift_ps)
            drift_rs = "~~~~" if drift_rs is None else '{0:.2f}'.format(drift_rs)
            leftconfidence = '{0:.0f}'.format(leftconfidence)
            rightconfidence = '{0:.0f}'.format(rightconfidence)
            caption = "{} m << {}% << [{} m]  >> {}% >> {} m".format(leftcurverad_rs, leftconfidence, drift_rs, rightconfidence, rightcurverad_rs)
            cv2.putText(latest, caption, (x, y), self.Font, 0.8, self.CaptionColor, self.CaptionThickness)
            self.__plot__(frame, latest, None, "Captioned", None)
            
        return latest
