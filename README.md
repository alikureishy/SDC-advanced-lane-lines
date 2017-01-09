<!--- Adding links to various images used in this document --->
[Thresholding]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration1.png "Thresholding"
[Detailed]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration2.png "Detailed"
[HighLevel-Green]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration3.png "High Level - Green"
[HighLevel-Red]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration4.png "High Level - Red"
[MappedLane]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration5.png
[StatsWriter]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration6.png "Caption showing lane statistics"
[Thresholding2]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration7.png "Thresholding"
[LaneFinder]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration8.png "Lane Finder Illustration"
[LaneFinder2]: https://github.com/safdark/advanced-lane-lines/blob/master/docs/images/illustration9.png "Lane Finder Illustration"

[![Mapped Lane][MappedLane]](https://youtu.be/jzAWMtA1zX8 "Click to see video on youtube")

## Advanced Lane Finding

### Overview

This was project # 4 of the Self Driving Car curriculum at Udacity. It was aimed at advanced lane detection for a front-facing camera on the car. No additional sensor inputs were utilized for this project.

The goals / steps of this project were the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply the distortion correction to the raw image.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view"). 
* Detect lane pixels and fit to find lane boundary.
* Determine curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

I've tried to make the utility extensible and configurable. All configuration settings involving locations of points on images have been expressed as a fraction of the 2 dimenions. So, for such configurations, no changes ar necessary when changing the input video frame size. A significant amount of time was spent building a 'framework' which could support the needs of the project, and to allow for such configurability. In as much as the parameters for this project were known to me, the implementation does a reasonably good job. However, a *lot* still remains to be cleaned up and refactored. Please bear this in mind during any inspection of the code base.

### Installation

This is a python utility requiring the following libraries to be installed prior to use:
* python (>= 3)
* numpy
* scikit-learn
* OpenCV3
* matplotlib

Here is a [sample output](https://www.google.com "advanced lane detection project output") produced by this utility on the project video.

### Execution

There are two utilities in this project. One is the calibrator (calibrator.py) that is to be run as a preparatory step prior to running the second, which is the lane mapper (lanemapper.py).

#### Image Calibration

The output of this utility run against a folder of images is stored in a file that is then used to undistort/redistort images during advanced lane detection. The utility is in the file calibrator.py. It is a command line utility, with a sample invocation as follows:

```
/Users/safdar/git/advanced-lane-detection/src> python3.5 calibrator.py -i ../camera_cal -o config/calibration.pickle
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

Note the '-o' parameter because the parameter used here will need to be provided in the configuration settings for the 'Lane Mapper' utility below. Please see the 'Implementation' section below for details.


#### Lane Mapper Utility

This utility is in the file lanemapper.py. It is also a command line utility, invoked as in the following example:

```
/Users/safdar/git/advanced-lane-detection/src> python3.5 lanemapper.py -i ../project_video.mp4 -o ../sample_out.mp4 -c config/lanemapper.json -x 1 -p
```
Note that the '-p' flag turns on the illustration (via a plot window) of various image transformations that each frame goes through -- the plot window is kept updated throughout. This is illustrated here:

![High level transformation sequence][HighLevel-Green]

Note: To not output these illustrations, remove the '-p' flag. Removing the -p flag will also cause the utility to run a lot faster. Though using this flag slows down processing, it also provides insight into the working of the utility. The illustrations can also be individually toggled in the config file (src/config/lanemapper.json). To enable additional details of the image transformations, go to the lanemapper.json file and search for the 'ToPlot' flags. Each component has that flag, and a value of '1' indicates that it is enabled, and '0' indicates it is disabled. Toggle the value for the components that you want to visualize, for example, the 'PerspectiveTransformer' or the 'Thresholder' etc. At present, only the 'StatsWriter' and 'Thresholder' are enabled. Thresholder illustrations are enabled at a high level only -- that is, only the final output is shown. Individual threshold transformations can also be enabled using the finer grained 'ToPlot' settings on each such threshold operation.

Here's the help menu:
```
###############################################
#                 LANE MAPPER                 #
###############################################
usage: lanemapper.py [-h] -i INPUT [-o OUTPUT] -c [CONFIGS [CONFIGS ...]]
                     [-s SELECTOR] [-x SPEED] [-d] [-p]

Lane Finder

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT              Path to image file, image folder, or video file.
  -o OUTPUT             Location of output (Will be treated as the same as
                        input type)
  -c [CONFIGS [CONFIGS ...]]
                        Configuration files.
  -s SELECTOR           Limit the pipeline to perform only specified # of
                        operations.
  -x SPEED              Speed (1 ,2, 3 etc) interpreted as 1x, 2x, 3x etc)
  -d                    Dry run. Will not save anything to disk (default:
                        false).
  -p                    Plot all illustrations marked as 'ToPlot' in the
                        config. (default: false).
```


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

Here is a detailed illustration that can be generated from this utility, using the pipeline above, and it is kept updated as each subsequent frame is processed:
![Detailed][Detailed]


A top level pipeline object is created, that sets up the processor pipeline after reading this configuration. Each processor listed above is expected to have a corresponding configuration 'section' further down in the JSON, as illustrated in each processor subsection below.

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
The output produced by this processor is depicted in the image below. It appears at the bottom of the video outputted by the utility:
![Statistics][StatsWriter]

The format/meaning of the stats printed above is:

```
{Curvature-Of-Left-Lane} m << {Confidence-In-Detected-Left-Lane}% << [{Drift-From-Center} m]  >> {Confidence-In-Detected-Right-Lane}% >> {Curvature-Of-Right-Lane} m
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
    "Thresholder": {
		"ToPlot": 1,
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
				},
				{
					"ToPlot": 1,
					"Operator": "AND",
					"Negate": 0,
					"Operands": [
				    	{"SobelY": { "Kernel": 3, "MinMax": [12,33], "Negate": 0, "ToPlot": 1}},				
						{
							"ToPlot": 1,
							"Operator": "OR",
							"Negate": 0,
							"Operands": [
						    	{"SobelX": { "Kernel": 3, "MinMax": [4,33], "Negate": 0, "ToPlot": 1}},
						    	{"SobelXY": { "Kernel": 3, "MinMax": [12,33], "Negate": 0, "ToPlot": 1}}
						    ]
						}
					]
				},
				{
					"ToPlot": 1,
					"Operator": "AND",
					"Negate": 0,
					"Operands": [
				    	{"SobelXY": { "Kernel": 3, "MinMax": [0,3], "Negate": 1, "ToPlot": 1}},
				    	{"SobelXY": { "Kernel": 3, "MinMax": [4,7], "Negate": 0, "ToPlot": 1}}
				    ]
				}
			]
		}
    },
```

Here's an illustration of the transformations generated by the Thresholder from the configuration above:
![Various thresholds applied to image][Thresholding]

And here's the same threshold pipeline applied to another video:
![Various thresholds applied to image][Thresholding2]

In the case of the project test video, color thresholding seemed sufficient to detect the lane lines. Most of the ambiguity was with the right lane, rather than the left yellow lane. Though the right lane was sufficiently detected in most cases, it is two regions of the highway that posed a slight problem. There is room for improvement. The hope has been, as should be evident from the configurability of this system, to spend some more time to tweak and tune the parameters to find a more robust thresholding. However, as shall be obvious in the 'LaneFinder' section, a large part of this ambiguity was usually addressed by the lane finding algorithm, at least for the project test video. The challenge videos require further changes and enhancements not just to the thresholding expression but to some of the algorithmic nuances that I have highlighted in more detail in the 'Areas for improvement' section further down in this document.

Sobel thresholding, though potentially a useful tool, proved largely unnecessary for the test video. I see it being more useful in the challenge videos. The intention around the configurability, as mentioned, was precisely to be able to play around with various settings. It is my goal to polish up this configurability and come up with an expression that will work for different types of videos.


#### Perspective Transformer
This component, as is obvious, performs a perspective transformation of the input image. The 'DefaultHeadingRatios' setting is of the form '[X-Origin-Ratio, Orientation]' and in conjunction with the 'DepthRangeRatio', specifies the source points for transformation. The 'TransformRatios' setting is of the form '[XRatio, YRatio]' and is used to specify the transformed points desired. The order is [UpperLeft, UpperRight, LowerLeft, LowerRight]. All points are expressed as ratios of the length of the corresponding dimension. It transforms the persective from source to destination during upstream processing, and destination back to source during the downstream pipeline.

This configuration makes it easy to modify the perspective without needing to know the image size etc, since every point is expressed as a fraction of the corresponding dimension.

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
	"DynamicVerticalSplit": 0,
    	"CameraPositionRatio": 0.50
},
```

Here is an illustration of the way the lane search algorithm presently works. To see this illustration while running the utility, as already mentioned, flip the 'ToPlot' setting above to '1', and use the '-p' flag of the command line utility (lanemapper.py). This illustration was created by superposing various lane search metrics on top of a birds-eye view of the original lane. The reddish dots correspond to the peaks discovered, and their position relative to the slice represents the histogram value. The overlapping green boxes are the 2 types of search windows -- one based on the previous frame's peaks and the other based on the earlier slice's peak -- that are used to narrow down the search for individual peaks. There is a vertical separator identifying the left and right sections that the image is split into.

![Illustration of lane searching][LaneFinder]

In this other illustration (below), the 'SliceRatio' setting has been reduced to 0.05. This results in each slice having a width that is 5% of the vertical dimension, which means there are double the slices as compared to when the setting was 0.10 for the above illustration. Furthermore, note the windows that are shaded red. If for a given slice and side, the search window is green (as was the case for all windows in the previous illustration), it means that a peak was found within that window. If it is red, as is the case with several windows in this illustration below, it means that no peak was found within that window. Given the visual of the lane for this project, is not surprising that the left lane has a continuous sequence of peaks whereas the right lane does not. Despite the absence of right peaks however, as you can see, the algorithm is still able to discern the polynomial for the right lane. This and various other mechanisms used here are discussed in detail in the 'Algorithm / Heuristics' section below.

![Illustration of lane searching][LaneFinder2]


##### Algorithms / Heuristics

The lane detection process (and illustrations) above can be broken down into the following components, each using a different heuristic, and each tweakable through the 'LaneFinder' configuration settings listed above. In fact, there is almost a 1-1 correspondence between the configuration settings above, and the heuristics discussed below.

###### Horizontal slicing
This is controlled by the 'SliceRatio' parameter, that specifies the fraction of the vertical dimension (y dimension) that each horizontal slice should cover. The smaller the fraction, the more the slices, and higher the sensitivity of the lane detection. The larger the slices, the coarser the peaks, and lesser the sensitivity. It appeared that a fraction of 0.05 - 0.10 was rather effective for the first video. This may not be the case for the challenge videos, where the curvature of the lane lines is smaller, and changes more rapidly.

###### Horizontal search

This refers to the directional scan of the histogram calculated for each horizontal slice above, looking for the point with the highest magnitude of aggregated pixels. The 'SliceRatio' parameter essentially limits the magnitude of all such points along the histogram to within a [0-SliceSize] range, assuming binary pixel values.

However, a more restrictive heuristic can be defined by the 'PeakRangeRatios' parameter which is, as with other parameters, expressed as a tuple of fractions, representing the necessary, and the sufficient, magnitude (as a fraction of the SliceSize) thresholds for any given point on the histogram, in the direction of search, to either be dropped from consideration, or to be selected as the peak, respectively. Upon encountering such points, the decision regarding that point is final -- either it is the peak, or it isn't. Points that fall between these two numbers -- i.e, above the necessary threshold and below the sufficient magnitude -- are considered candidates, put to test by being compared against subsequent point values, until either the sufficient threshold is crossed, or scan ends, at which point the highest valued point is labeled as the peak. If no point is found through a scan, the algorithm registers a non-existent peak for that scan.

The 'CameraPositionRatio' setting specifies the position of the camera, relatiave to the car. This has been set to 50 % with the assumption that the camera is more-or-less at the center of the car, and therefore, that the left and right of the car is balanced, relative to the camera. The setting can accommodate the scenario wherein it is not balanced too. This knowledge helps determine the position of the car relative to the calculated center of the lane, i.e, the 'drift'. If the camera is not at the center of the car, then that needs to be factored into the calculation of the 'drift'.

The search progresses outward from the center of the lane, comprising of one scan from mid -> left extreme, and another scan from mid -> right extreme. The decision of this 'mid point' for the adjacent scans is configurable via the 'DynamicVerticalSplit' setting. When switched off, the left-right partitioning of the lane is *always* done at the center of the X-dimension. It's worth noting here that actually, the center of the lane moves from frame to frame. So, using a fixed value for the midpoint of the horizontal slice is not optimal. The 'DynamicVerticalSplit' setting allows one to either use the fixed value above, or to determine the partition center dynamically. If set to '1', then the determination of the partition is made dynamically on each frame, by calculating the mean of the fitted x values of both the first slice and the last slice of the previous frame - i.e, the mean of 4 points. This is so that, as far as possible, the lanes don't bleed over to the other side further down the road. At present, this setting is switched off in the configuration, so a fixed partition point is used for all frames.


###### Aggressive peak search bounding
In addition to the 'PeakRangeRatios' heuristic, the scan of either side of a histogram can be further optimized by looking for the peak within a narrower horizontal range (dictated by the 'PeakWindowRatio' config param), and centered around a combination of:
- the position of the peak on the same side of the *earlier* slice (for the same frame), and
- the position of the peak for the same side of the *subsequent* slice (predicted by the polynomial of the lane from the previous frame).
More specifically, the smallest window discernible from these positions is utilized. This may seem rather limiting, but happens to achieve good results on the test video. And if neither of these are available, then the search is expanded to the entire span of the relevant side of the histogram. This aggressive narrowing of the search space also decreases the impact of noise. And it is adaptive enough such that if either of the above centers was detected erroneously, it would impact the confidence of the lane detected in that frame, decreasing the probability of an erroneous detection in the subsequent frame.

There is a risk of getting caught detecting points that are not along either of the lanes. This can be solved by:
- using an improved heuristic based on the expected width (in pixels) of the lane (discussed in the limitations section), or
- improving the thresholding expression to eliminate or minimize this noise.

###### Lookback period and lane smoothing
Since detection is not perfect, every new frame may bring with it some surprises -- either missing peaks, or inaccurate peaks that deviate from the expectation. The 2nd illustration above with the missing peaks on the right lane is an example of this. Notice that despite the missing peaks, the lane is still discernable. It is also essential to smooth out the detection of lanes to be robust to such surprises.

A convenient heuristic for filling in these missing peaks, and for smoothing, is to utilize the discovered peaks from previous frames in addition to those discovered from the latest frame, when trying to fit a polynomial to the lane. This avoids any sudden jerky projections of the lane lines, bringing out a smoother progression of the lane mapping. Note that only the previous *discovered* peaks are used, not the peaks fitted by the corresponding polynomial function.

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

Furthermore, as is illustreated below, the lane filler also detects when the car drifts too far to the left or right of the lane's center, and accordingly changes the lane coloring between Green (for acceptable drift) to Red (for unacceptable drit). The threshold between aceptable and unacceptable drift is controlled by the 'DriftToleranceRatio' setting, expressed in terms of a ratio of the X-dimension of the image.

![Dangerous drift][HighLevel-Red]

### Areas for Improvement & Potential Failure Scenarios:

Areas where this project could improve are discussed below, outlining scenarios where the algorithm would likel fail. I could not implement these options due to time considerations, but I might revisit them further "down the road' (pun intended).

#### Mid-Line for Left/Rigth Peak Categorization

Presently, the algorithm for searching for histogram peaks searches on each side of a straight vertical 'center' line that is calculated based on the fitted X-values of the first and last slice of the previous frame. However, the lanes could at times have such a short radius of curvature that the histogram peaks further down on each lane could spill over to the adjacent lane's search region causing the lane peaks to be inaccurately categorized by the search algorithm. This would most certainly be the case if the turns are very sharp.

A more robust solution for this situation would be to not use a straight line separator for left/right lanes, but rather, to use another 2nd order polynomial fit for the midpoints of the 2 lanes as well (in the same way as was used to fit each lane). Alternatively, the points for this mid-line polynomial could be obtained by averaging the fitted X-values from the previous frame. Using this fitted center line would be a far more accurate approach for meandering or curvy roads.

#### Erroneous lane noise elimination using pixel-to-standard-lane-width translation

Lane detection at present does not utilize the expected lane width, established by US road standards. This information, when combined with the confidence metric discussed earlier, could greatly improve the accuracy of the detection by allowing the system to choose the best option (or drop the unlikely option) in case of ambiguity.

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
