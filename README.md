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

### Areas for Improvement:

Areas where this project could improve are discussed below. I could not implement these options due to time considerations, but I might revisit them 'further down the road', pun intended.

#### Mid-Line for Left/Rigth Peak Categorization

Presently, the algorithm for searching for histogram peaks searches on each side of a vertical 'center' line that is calculated to be the midpoint of the X-dimension. There is a naive assumption here that the center of the lane is always more or less at the center of the camera. Clearly, this is a limiting assumption since the car is almost never right at the center of the screen. Furthermore, even if the car were at the center, the lanes could at times have such a short radius of curvature that the histogram peaks further down on each lane could spill over to the adjacent lane's search region causing the lane peaks to be inaccurately categorized by the search algorithm.

A simple, yet suboptimal solution, is to use the center of the lane from the previous frame instead of using the midpoint of the X-dimension, when partitioning the image into the left and right regions for searching for lane peaks. This is easiliy obtained by performing a mean of the positions of the two lanes at the bottom of the image.

A more robust solution, especially to avoid miscategorizing peaks further down on each lane, would be to calculate a polynomial fit of the midpoint of the 2 lanes (using a 2nd order polynomial in the same way as was used to fit each lane). The points for this mid-line polynomial would be obtained by averaging the peaks obtained from each slice of the frame. A confidence could be associated to this mid-line based on the lower of the confidence levels of the two lanes for that frame. Using this fitted center line would be the most accurate approach for this problem, in my view, particularly for meandering or curvy roads.

#### Dynamic identification of perspective points

One option that was mentioned previously is to dynamically adjust the perspective used for the perspective transform, the goal being to advance the perspective only as far as not to include more than one curve in the transformation. The disadvange of this approach, as mentioned, would be that the car would have to slow down (since its 'vision' is now very short), or risk 


#### Using a 3rd order polynomial

Lanes that are particularly curvy or meandering may not always fit to a 2nd order polynomial. This is because the stretch of the lane over the same line of sight might include not just one curve, but two curves. In fact, in extreme circumstances, particularly when the camera is higher above the ground, multiple curves might be visible within the line of sight.

One option that was mentioned previously is to dynamically adjust the perspective used for the perspective transform, the goal being to advance the perspective only as far as not to include more than one curve in the transformation. The disadvange of this approach, as mentioned, would be that the car would have to slow down.

Another alternative, instead of shortening the perpspective, is to use a higher order polynomial to fit the discovered peaks. This would allow the car to potentially not have to slow down as much, and to also make higher confidence driving decisions.
