'''
Created on Jan 1, 2017

@author: safdar
'''
# Stages of lane detection:


# Stage 1:
#    - Detect only starting points of lanes (x intercepts)
#    - 

# Takes a set of lane candidates
# and filters out those that don't
# satisfy the criteria for lane lines
class LaneFilterParams(object):
    LeftSlopeRange = 'LeftSlopeRange'
    RightSlopeRange = 'RightSlopeRange'
    LeftInterceptRatios = 'LeftInterceptRatios'
    RightInterceptRatios = 'RightInteceptRatios'
    DepthRangeRatio = 'DepthRangeRatio'

# Takes a set of candidate lanes and
# fits them to a polynomial function
class LaneFitterParams(object):
    pass

def extractlanes1(lines, lanefilter):
    left_slope_range = lanefilter.get(HoughFilterParams.LeftSlopeRange, None)
    right_slope_range = lanefilter.get(HoughFilterParams.RightSlopeRange, None)
    left_span_ratio = lanefilter.get(HoughFilterParams.LeftSpanRatios, [])
    right_span_ratios = lanefilter.get(HoughFilterParams.RightSpanRatios, [])
    y_range_ratios = lanefilter.get(HoughFilterParams.DepthRangeRatio, [0.95, 0.70])
    

    

    return None


############################

def STREAMER(file):
    pass

def SPACER(gen, orig=RGB, target=HSV):
    pass

def RESIZER(gen, xratio=X, yratio=Y):
    pass

def VSTACK(*c_igens):
    pass

def HSTACK(*c_igens):
    pass

def DSTACK(*c_igens):
    pass

def INRANGE(m_c_igen, low=[4,3,2], high=[10,2,3]):
    pass

def OFRANG(gen, low=[4,3,2], high=[10,2,3]):
    pass

def OR(*m_b_igens):
    pass

def AND(*m_b_igens):
    pass

def PLOT(*m_c_igens):
    pass

def WRITE(*m_c_igens):
    pass


print (\
       WRITE(\
             PLOT(\
                  
                      RESIZER(\
                              SPACER(\
                                     STREAMER(\
                                              file
                                              )


