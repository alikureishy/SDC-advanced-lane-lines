## Advanced Lane Finding

### Overview

This was project # 4 of the Self Driving Car curriculum at Udacity. It was aimed at advanced lane detection for a front-facing camera on the car. No additional sensor inputs were utilized for this project.

An overarching theme of this project was to make it extensible and highly configurable, though the time provided for this implementation has left some ground to still cover. Nevertheless, I have placed a heavy emphasis -- and will continue to be the emphasis -- for this utility to require minimal configuration changes when the input video settings change (eg., the frame size, frame rate, etc). A significant amount of time was spent building a framework of sorts, to allow for such configurability. In as much as the parameters for this project were known to me, the implementation so far does a pretty good job. However, a *lot* still remains to be cleaned up and refactored. Please bear this in mind during any inspection of the code base.

The goals / steps of this project were the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply the distortion correction to the raw image.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view"). 
* Detect lane pixels and fit to find lane boundary.
* Determine curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

### Installation

This is a python utility requiring the following libraries to be installed prior to use:
* python (>= 3)
* numpy
* scikit-learn
* OpenCV3
* matplotlib

### Execution

#### Lane Mapper Utility

This is reflected in the file lanemapper.py. It is a command line utility, invoked as follows:

```
/Users/safdar/advanced-lane-detection/src> python3.5 lanemapper.py [-h] -i INPUT [-o OUTPUT] -c [CONFIGS [CONFIGS ...]]
                     [-s SELECTOR] [-x SPEED] [-d]
```

Here's the help menu:
```
###############################################
#                 LANE FINDER                 #
###############################################
usage: lanemapper.py [-h] -i INPUT [-o OUTPUT] -c [CONFIGS [CONFIGS ...]]
                     [-s SELECTOR] [-x SPEED] [-d]

Lane Finder

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT              Path to image file, image folder, or video file.
  -o OUTPUT             Location of output (Will be treated as the same as
                        input type)
  -c [CONFIGS [CONFIGS ...]]
                        Configuration files.
  -s SELECTOR           Short circuit the pipeline to perform only specified #
                        of operations.
  -x SPEED              Speed (1 ,2, 3 etc) interpreted as 1x, 2x, 3x etc)
  -d                    Dry run. Will not save anything to disk (default:
                        false).
```


#### Image Calibration

This is reflected in the file calibrator.py. It is a command line utility, invoked as follows:

```
/Users/safdar/advanced-lane-detection/src> python3.5 calibrator.py [-h] -i INPUT -o OUTPUT [-s SIZE] [-t TEST] [-p] [-d]
```

Here's the help menu:
```
###############################################
#                 CALIBRATOR                  #
###############################################
usage: calibrator.py [-h] -i INPUT -o OUTPUT [-s SIZE] [-t TEST] [-p] [-d]

Camera Calibrator

optional arguments:
  -h, --help  show this help message and exit
  -i INPUT    Path to folder containing calibration images.
  -o OUTPUT   Location of output (Will be treated as the same as input type)
  -s SIZE     Size of the checkboard : (horizontal, vertical)
  -t TEST     Test file to undistort for visual verification.
  -p          Plot the chessboard with dots drawn (default: false).
  -d          Dry run. Will not save anything to disk (default: false).
  ```

Note the '-o' flag because the parameter used here will need to be provided in the configuration settings for the 'Lane Mapper' utility above. Please see the 'Implementation' section below for details.


### Design

The following sections discuss the implemented components/algorithms of this project. Each component's configuration is illustrated for further clarity. The goal of the configuration sections below was to separate the user-configurable parts from the actual code, though basic familiarity with JSON files would still be expected of any user. A look at the configuration should serve as a convenient segue into the implementation details.

#### Pipeline
This lays out the processor pipeline that each frame is put through prior to being returned to the user for lane visualization. Each processor supports a 'ToPlot' setting that dictates whether the illustrations produced by the processor are to be displayed to the user, or whether they are to be kept silent. In essence, it serves as a sort of 'silencing' flag ('0' indicating silence).

```
{

"Pipeline": [
    	"StatsWriter",
    	"Undistorter",
    	"Thresholder",
    	"PerspectiveTransformer",
    	"LaneFinder",
    	"LaneFiller"
    ],
```

There's not much to discuss here. A top level pipeline object is created, that sets up the processor pipeline after reading this configuration. Each processor listed above is expected to have a corresponding configuration 'section' further down in the JSON, as illustrated in each processor subsection below.

In essence, for the configuration above, the following pipeline is generated:
```
StatsWriter --> Undistorter --> Thresholder --> PerspectiveTransformer --> LaneFinder --> LaneFiller
                                                                                              V
                                                                                              V
StatsWriter <-- Undistorter <-- Thresholder <-- PerspectiveTransformer <-- LaneFinder <-- LaneFiller 
```
The first line is the 'upstream' pipeline, and the lower line is the 'downstream' pipeline, which is always a reversal of the upstream, based on the Chain Of Responsibility design pattern.

#### Stats Writer
This is a downstream processor that writes various pipeline stats to the final processed image. It is placed first, but actually kicks in last on the unwind of pipeline stack. The pipeline stats in this case are generated by the 'LaneFinder' component that kicks in during upstream processing of the pipeline, which is available to this processor downstream.

```
"StatsWriter": {
		"ToPlot": 0
},
```

#### Undistorter
This is an upstream and downstream processor that respectively undistorts/redistorts the image based on calibration data generated through a different utility ('calibrator.py'), which is expected to have been previously saved to the 'CalibrationFile' below. The image is UNdistorted on the upstream path, and re-distorted on the downstream path before being written out to disk.

```
"Undistorter": {
		"ToPlot": 0,
        "CalibrationFile": "config/calibration.pickle"
},
```

#### Thresholder
This is an upstream processor that is one of the most configuration-heavy components in the pipeline. It is still a W-I-P but at present supports expressions combining Color- and Sobel- based transformations of the images in any number of desired ways (including multi-level nesting). The image that is output by this processor at present is necessarily a binary image.

```
"Thresholder": {
		"ToPlot": 0,
    	"HoughFilter": {
    		"Rho": 2, "Theta": 0.0174, "Threshold": 100, "MinLineLength": 75, "MaxLineGap": 30,
	    	"LeftRadianRange": [-0.95, -0.50], "RightRadianRange": [0.50, 0.95], "DepthRangeRatio": [0.95, 0.70]
    	},
		"Term":
		{
			"ToPlot": 1,
			"Operator": "OR",
			"Negate": 0,
			"Operands": [
				{
					"ToPlot": 1,
					"Operator": "AND",
					"Negate": 0,
					"Operands": [
				    	{"Color": { "Space": "HLS", "Channel": 0, "MinMax": [50,200], "Negate": 1, "ToPlot": 1}},
				    	{"Color": { "Space": "RGB", "Channel": 0, "MinMax": [50,200], "Negate": 1, "ToPlot": 1}}
				    ]
				},
				{
					"ToPlot": 1,
					"Operator": "AND",
					"Negate": 0,
					"Operands": [
				    	{"Color": { "Space": "HLS", "Channel": 2, "MinMax": [50,200], "Negate": 0, "ToPlot": 1}},
				    	{"Color": { "Space": "RGB", "Channel": 1, "MinMax": [50,200], "Negate": 1, "ToPlot": 1}}
				    ]
				}
			]
		}
},
```
In the case of the project test video, color thresholding seemed sufficient to detect the lane lines. Most of the ambiguity was with the right lane, rather than the left yellow lane. Though the right lane was sufficiently detected in most cases, it is two regions of the highway that posed a slight problem that I could not fully resolve at present. The hope has always been, as should be evident from the configurability of this system, that I spend some more time to tweak and tune the parameters to find a more robust thresholding. However, as shall be obvious in the 'LaneFinder' section, a large part of this ambiguity was usually addressed by the lane finding algorithm, at least for the project test video. The challenge videos require further changes and enhancements not just to the thresholding expression but to some of the algorithmic nuances that I have highlighted in more detail in the 'Areas for improvement' section further down in this document.

Sobel thresholding, though potentially a useful tool, proved largely unnecessary for the test video. I see it being more useful in the challenge videos. The intention around the configurability, as mentioned, was precisely to be able to play around with various settings. It is my goal to polish up this configurability and come up with an expression that will work for different types of videos.


#### Perspective Transformer
This component, as is obvious, performs a perspective transformation of the input image. The 'DefaultHeadingRatios' setting is of the form '[X-Origin-Ratio, Orientation]' and in conjunction with the 'DepthRangeRatio', specifies the source points for transformation. The 'TransformRatios' setting is of the form '[XRatio, YRatio]' is used to specify the transformed points desired. The order is [UpperLeft, UpperRight, LowerLeft, LowerRight]. All points are expressed as ratios of the length of the corresponding dimension. It transforms the persective from source to destination during upstream processing, and destination back to source during the downstream pipeline.

```
"PerspectiveTransformer": {
      "ToPlot": 0,
      "DefaultHeadingRatios": [
        	[0.20, -1.2],
        	[0.86, 1.60]
      ],
      "DepthRangeRatio": [0.99, 0.63],
      "TransformRatios": [
        	[0.25, 0.0],
        	[0.75, 0.0],
        	[0.25, 1.0],
        	[0.75, 1.0]
      ]
},
```

#### Lane Finder
This upstream processor locates the lane lines in the frame. It is where all the lane detection algorithms are used. Data discovered about the current frame, and a few of the previous frames (as history), is output by this component, for subsequent processors in the pipeline to utilize. Specifically, it generates data about the left and right lane polynomial fits, the associated X/Y points observed (as well as the fit-generated X/Y points) for each lane. It also detects the position of the car relative to the center of the lane. Confidence levels are also associated with each discoved lane line, for each frame.

```
"LaneFinder": {
	"ToPlot": 0,
	"SliceRatio": 0.10,
    	"PeakRangeRatios": [0.10, 0.50],
    	"PeakWindowRatio": 0.05,
    	"LookBackFrames": 4,
    	"CameraPositionRatio": 0.50
},
```

##### Algorithms / Heuristics

The lane detection procedure can be broken down into the following components, each using a different heuristic, and each tweakable through the configuration settings illustrated above. In fact, there is almost a 1-1 correspondence between the configuration settings above, and the heuristics below.

###### Horizontal slicing
This is controlled by the 'SliceRatio' parameter, that specifies the fraction of the vertical dimension (y dimension) that each horizontal slice should cover. The smaller the fraction, the more the slices, and higher the sensitivity of the lane detection. The larger the slices, the coarser the peaks, and lesser the sensitivity. It appeared that a fraction of 0.05 - 0.10 was rather effective for the first video. This may not be the case for the challenge videos, where the curvature of the lane lines is smaller, and changes more rapidly.

###### Horizontal search

This refers to the directional scan of the histogram calculated for each horizontal slice above, looking for the point with the highest magnitude of aggregated pixels. The 'SliceRatio' parameter essentially limits the magnitude of all such points along the histogram to within a [0-SliceSize] range, assuming binary pixel values.

However, a more restrictive heuristic can be defined by the 'PeakRangeRatios' parameter which is, as with other parameters, expressed as a tuple of fractions, representing the necessary, and the sufficient, magnitude (as a fraction of the SliceSize) thresholds for any given point on the histogram, in the direction of search, to either be dropped from consideration, or to be selected as the peak, respectively. Upon encountering such points, the decision regarding that point is final -- either it is the peak, or it isn't. Points that fall between these two numbers -- i.e, above the necessary threshold and below the sufficient magnitude -- are considered candidates, put to test by being compared against subsequent point values, until either the sufficient threshold is crossed, or scan ends, at which point the highest valued point is labeled as the peak. If no point is found through a scan, the algorithm registers a non-existent peak for that scan.

The search progresses outward from the center of the X-dimension, comprising of one scan from mid -> left extreme, and another scan from mid -> right extreme. The decision of this 'mid point' for the adjacent scans is configurable via the 'CameraPositionRatio' setting. This has been set to 50 % of the X dimension at present, assuming the camera is at the center of the car, but can accommodate the scenario wherein it is not. This setting is necessary so as to determine the position of the car relative to the center of the lane, i.e, the 'drift'. If the camera is not at the center of the car, then that needs to be factored into the calculation of the 'drift'.

###### Aggressive peark search bounding
In addition to the 'PeakRangeRatios' heuristic, the scan of either side of a histogram can be further optimized by looking for the peak within a narrower horizontal range (dictated by the 'PeakWindowRatio' config param), and centered around a combination of:
- the position of the peak on the same side of the *earlier* slice (for the same frame), and
- the position of the peak for the same side of the *subsequent* slice (predicted by the polynomial of the lane from the previous frame).
More specifically, the smallest window discernible from these positions is utilized. This may seem rather limiting, but happens to achieve good results on the test video. And if neither of these are available, then the search is expanded to the entire span of the relevant side of the histogram. This aggressive narrowing of the search space also decreases the impact of noise. And it is adaptive enough such that if either of the above centers was detected erroneously, it would impact the confidence of the lane detected in that frame, decreasing the probability of an erroneous detection in the subsequent frame.

There is a risk of getting caught detecting points that are not along either of the lanes. This can be solved by:
- using an improved heuristic based on the expected width (in pixels) of the lane (discussed in the limitations section), or
- improving the thresholding expression to eliminate or minimize this noise.

###### Lookback period and lane smoothing
Since detection is not perfect, every new frame may bring with it some surprises. It is essential to smooth out the detection of lanes to be robust to these surprises. A convenient approach to smoothing is to utilize the discovered peaks from previous frames in addition to those discovered from the latest frame, when trying to fit a polynomial to the lane. This avoids any sudden jerky projections of the lane lines, bringing out a smoother progression of the lane mapping. Note that only the previous *discovered* peaks are used, not the peaks fitted by the corresponding polynomial function.

The approach of using previously discovered peaks has another advantage, which is that it renders a natural weighting of discovered peaks toward lane mapping. Frames/lanes with fewer discovered peaks will contribute fewer points toward fitting a polynomial for not just their own lanes, but also the lanes of subsequent frames (upto a limit specified by the 'LookbackPeriod' parameter). Consequently, frames with a larger number of peaks will carry higher weightage, as they should.

The extent of this influence is determined by the 'LookbackPeriod' config setting. The higher this number, the further back the algorithm looks when mapping lane lines, and the smoother the progression of the lanes with each subsequent frame. However, the disadvantage from this inertia is that the algorithm will adapt slower to lane changes, and worse, to correcting erroneous detections. I have used a lookback period of about 4 frames, which I found achieves a balance between too much inertia and smoothness.

###### Peak detection & Confidence
Each slice is ideally expected to generate 2 peaks -- one on the left and the other on the right. This is not always the case, however. Nevertheless, even with a few such peaks discerned from the slices across a given frame, it is possible to fit a polynomial function to then determine the expected lane line. Once the functions have been fitted, it can be used to 'fill-in' unknown X-values that can facilitate the detection of subsequent peaks in the following frames (as discussed above), as well as paint between the disambiguated lane lines.

However, each polynomial fit is only as reliable as the points feeding it. This reliability is difficult to ascertain immediately, but generally becomes apparent over subsequent frames. This is because, assuming the thresholding function minimizes noise, any erroneous lane detection will narrow the search window for seeking out subsequent peaks to within that erroneous area, yielding fewer and fewer peaks in subsequent frames. The fewer the number of peaks in a given lane detection, the lower its contribution toward detecting new lanes.


#### Lane Filler
This downstream processor takes the lane and car data generated by the 'LaneFinder' and 'fills' in the lane.

```
"LaneFiller": {
	"ToPlot": 0,
	"LaneConfidenceThreshold": 0.40,
	"DriftToleranceRatio": 0.05,
	"SafeColor": [152, 251, 152],
    	"DangerColor": [255,0,0]
}
```
This component is also responsible for selecting which lanes to draw, based on the confidence level associated with each lane from the current frame. A threshold is utilized, called 'LaneConfidenceThreshold', that determines the minimum confidence level associated with the lane in order for it to be accepted and drawn by this component. The behavior obtained from this logic is that no lane will be drawn until *both* the left and right lanes satisfy this minimum threshold. Once that threshold is met, the component will continue using the corresponding polynomial fit of each side of the lane to paint the lane's interior, until such time as the new data for either or both of the lanes satisfies the threshold, at which point it paints the lane interior using the updated lane fit(s). This makes the algorithm able to adapt to situations when no new information of sufficient confidence is obtained from the LaneFinder, because in such cases, it continues to use the last high-confidence lane information. This applies to each side of the lane. So, it's possible that one side gets updated, while the other remains the same. Either way, once it starts painting the lane, there is never a period where the lane can vanish.

### Areas for Improvement & Potential Failure Scenarios:

Areas where this project could improve are discussed below, outlining scenarios where the algorithm would likel fail. I could not implement these options due to time considerations, but I might revisit them further "down the road' (pun intended).

#### Mid-Line for Left/Rigth Peak Categorization

Presently, the algorithm for searching for histogram peaks searches on each side of a vertical 'center' line that is calculated to be the midpoint of the X-dimension. There is a naive assumption here that the center of the lane is always more or less at the center of the camera. Clearly, this is a limiting assumption since the car is almost never right at the center of the screen. Furthermore, even if the car were at the center, the lanes could at times have such a short radius of curvature that the histogram peaks further down on each lane could spill over to the adjacent lane's search region causing the lane peaks to be inaccurately categorized by the search algorithm.

A simple, yet suboptimal solution, is to use the center of the lane from the previous frame instead of using the midpoint of the X-dimension, when partitioning the image into the left and right regions for searching for lane peaks. This is easiliy obtained by performing a mean of the positions of the two lanes at the bottom of the image.

A more robust solution, especially to avoid miscategorizing peaks further down on each lane, would be to calculate a polynomial fit of the midpoint of the 2 lanes (using a 2nd order polynomial in the same way as was used to fit each lane). The points for this mid-line polynomial would be obtained by averaging the peaks obtained from each slice of the frame. A confidence could be associated to this mid-line based on the lower of the confidence levels of the two lanes for that frame. Using this fitted center line would be the most accurate approach for this problem, in my view, particularly for meandering or curvy roads.

#### Erroneous lane noise elimination using pixel-to-standard-lane-width translation



#### Dynamic identification of perspective points

Depending on the camera height relative to the road, and the contour of the road, the points used to transform the perspective for lane detection may vary. At present, a static set of points is being utilized, which assumes that both the above factors will remain static.

One option to avoid this limitation is to dynamically adjust the perspective used for the perspective transform, the goal being to (a) consistently obtain mostly parallel lane lines when scanning the transformation perspective, and (b) to advance the perspective only as far as not to include more than one curve in the transformation.


#### Using a 3rd order polynomial

Lanes that are particularly curvy or meandering may not always fit to a 2nd order polynomial. This is because the stretch of the lane over the same line of sight might include not just one curve, but two curves. In fact, in extreme circumstances, particularly when the camera is higher above the ground, multiple curves might be visible within the line of sight.

One option that was mentioned previously is to dynamically adjust the perspective used for the perspective transform, the goal being to advance the perspective only as far as not to include more than one curve in the transformation. The disadvange of this approach, as mentioned, would be that the car would have to slow down.

Another alternative, instead of shortening the perpspective, is to use a higher order polynomial to fit the discovered peaks. This would allow the car to potentially not have to slow down as much, and to also make higher confidence driving decisions.

#### Adaptive window for limiting peak searches

Presently, a static window is used to determine the bounds of the points used to detect a histogram peak, relative to the location of the peak in the slice right below the present slice, or the peak in the subsequent slice of the previous frame. Though these approaches allow a more efficient scan, it is possible to get stuck looking for a lane close to an erroneous lane or peak that was previously detected. To avoid this, it might be beneficial to increase the window size proportional to the confidence of the previously detected lane, or the confidence of the peaks obtained in the slices below. The lower the confidence, the larger the window becomes, upto a maximum size of the search region itself. The higher the confidence, the smaller the window gets, upto a minimum of the configured window size.

### Open Defects

I will get to these when time permits. Until then, am calling them out here. Please see the 'Issues' section of this github repository for further details.

* Performance of this utility is below par at the moment. Output from performance profiling suggests the culprit is the extensive use of matplotlib to illustrate the transformations/processing steps for each frame in the video. Switching off illustration speeds up performance significantly, but not sufficiently enough to ensure real-time detection during actual use on the road.

* Insufficient error checking. Since this is not a commercial use utility, emphasis was not given to ensuring producing descriptive error messages. If you choose to run this utility, but face issues, please feel free to create an 'Issue' for this project.
