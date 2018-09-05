# **Advanced Lane Finding Project**

### [Jupyter Notebook (HTML)](P2.html)

[//]: # (Image References)

[image0]: ./output_images/chessboard_img.jpg    "Chessboard Corners"
[image1]: ./output_images/undist_img.jpg        "Undistorted"
[image2]: ./output_images/pipeline1.jpg         "Pipeline 1"
[image3]: ./output_images/pipeline2.jpg         "Pipeline 2"
[image4]: ./output_images/pipeline3.jpg         "Pipeline 3"
[image5]: ./output_images/pipeline4.jpg         "Pipeline 4"
[image6]: ./output_images/windowed_img.jpg      "Windowed"
[image7]: ./output_images/posterior_img.jpg     "Windowed from Posterior"
[image8]: ./output_images/filled_lane_img.jpg   "Filled Lanes"
[image9]: ./output_images/processed_img.jpg     "Full Processed Image"
[video0]: ./project_video_output.mp4            "Project Video"
[video1]: ./challenge_video_output.mp4          "Challenge Video"
[video2]: ./harder_challenge_video_output.mp4   "Harder Challenge Video"

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.



### [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

---

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is contained in the first code cell of the [IPython notebook (HTML)](P2.html) located in `./P2.html`.  

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `initial_obj_pts` is just a replicated array of coordinates, and `obj_pts` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `img_pts` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  Those chessboard corners are visible here:

![alt text][image0]

I then used the output `obj_pts` and `img_pts` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera( )` function.  I applied this distortion correction to the test image using the `cv2.undistort( )` function in the `undistort_image( )` function and obtained this result:

![alt text][image1]

### Pipeline (single images)

#### 1. Provide an example of a distortion-corrected image.

To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one:
![alt text][image1]

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

I used a combination of color and gradient thresholds to generate a binary image in the following functions in `P2.ipynb`:
* `abs_sobel_thresh( )`

![alt text][image2]

* `mag_sobel_thresh( )`
* `dir_threshold( )`

![alt text][image3]
* `hls_s_select( )`
* `hls_l_select( )`

![alt text][image4]

The different thresholding functions are shown in a form similar to those used in the lecture notes. The `pipeline( )` function is defined showing use of only the `hls_s_select( )` and `hls_l_select( )` thresholding for the final pipeline result. Thresholds of `[ 110, 255 ]` and `[ 230, 255 ]` are used respectively.  Pipeline shown below:
![alt text][image5]

#### 3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform includes a function called `unwarp_image( )`, which appears in `P2.ipynb`.  The `unwarp_image( )` function takes as inputs an image (`img`), and defines source (`src`) and destination (`dst`) points.  I chose the hardcode the source and destination points in the following manner:

```python
def unwarp_image( img, plot='yes' ):

# Define image height and width
h, w = img.shape[:2]

# Define source and destination points for transform
src = np.float32([ ( 575, 464), ( 707, 464 ), ( 258, 682 ), ( 1049, 682 ) ] )
dst = np.float32([ ( 450, 0), ( w - 450, 0 ), ( 450, h ), ( w - 450, h ) ] )
```
I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image (see notebook for transformed images).

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

The functions `fit_sliding_window( )` and `fit_window_with_posterior( )` fit a  polynomial to both right and left lane lines.  The `fit_sliding_window( )` function computes a histogram of the bottom half of the image (as shown below).  It then finds the lower-most x pixel position of the left and right lane lines.  This can be considered the base of the lane line.  The function then identifies ten windows of identified lane pixels.  Each window is centered on the midpoint of the pixels from the window below.  This tracks lane lines up to the top of the binary image:

![alt text][image6]

The image above shows the histogram generated by `fit_sliding_window( )` with the resulting base points for the left and right lanes clearly visible:

The `fit_window_with_posterior( )` function performs a similar task as `fit_sliding_window( )`, but speeds up the search process by leveraging a previous fit, e.g. from a previous frame.  The function only searches for lane pixels within a certain range of that fit and if present tracks them in the same manner.  The image below demonstrates this - the green shaded area is the range from the previous fit, and the yellow lines and red and blue pixels are from the current image:

![alt text][image7]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in `get_radius_of_curvature( )` in `P2.ipynb`.  In this function, the two fitted lines are compared with a fixed reference in the bottom-most y-position of the car.  It is shown below:

```python
radius_l = ( ( 1 + ( 2 * new_fit_l[0] * max_y * m_per_pix_y + new_fit_l[1] ) ** 2 ) ** 1.5 ) \
        / np.absolute( 2 * new_fit_l[0] )
radius_r = ( ( 1 + ( 2 * new_fit_r[0] * max_y * m_per_pix_y + new_fit_r[1] ) ** 2 ) ** 1.5 ) \
        / np.absolute( 2 * new_fit_r[0] )
```

By factoring by a transfer coefficient from pixels to meters, `m_per_pix_y`, the radius can then be calculated.  This method was inspired by [this approach](https://www.intmath.com/applications-differentiation/8-radius-curvature.php).

The position of the vehicle with respect to the center of the lane is calculated with the following lines of code:

```python
lane_center_position = ( r_fit_intercept + l_fit_intercept ) / 2
center_dist = (car_position - lane_center_position) * x_meters_per_pix
```

where `r_fit_intercept` and `l_fit_intercept` are the x-intercepts of the right and left fits, respectively.  The car position is the difference between the image midpoint and these intercept points.

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

The function `draw_lane_data( )` in `P2.ipynb` shows takes in a piped image and provides a painted lane area, along with radius of curvature and centerline data.  Here is an example of my result on a test image:

![alt text][image8]

The final functions `process_image( )` and `process_video( )` contain the fully enabled pipelines and are used to generate images and videos:

![alt text][image9]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Project video:          [video0](./project_video_output.mp4)

Challenge video:        [video1](./challenge_video_output.mp4)         

Harder challenge video: [video2](./harder_challenge_video_output.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

As shown in the videos, the approach that I took works well in the project video but breaks down rather quickly with a non-uniform road and/or a high variance in lighting.  In the challenge video, there is an uneven lift of asphalt in the road which causes issues in the gradient detection.  In the harder challenge video, the foliage provides alternating shaded and sunlit views of the road, further obstructing the hard-coded thresholds in the processing pipeline.  To correct these, the thresholds would have to be adjusted to be more variable, and perhaps a combination of varying filters could be employed based on current road conditions.

#### 2. Contributions
I would like to thank @jeremy-shannon for the great visualization ideas he provided in his [code base on GitHub](https://github.com/jeremy-shannon/CarND-Advanced-Lane-Lines).
