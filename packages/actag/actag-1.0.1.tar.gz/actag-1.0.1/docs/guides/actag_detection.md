# Detecting AcTags

![Alt text](../../actag_families/image_files/example_images/BadgeFigureJustDetection.png "AcTags detected by a camera and a sonar.")

AcTags are fiducial markers that can be detected through both light and sound. Detection through light is achieved by taking advantage of the contrast between the dark acoustic foam and the light aluminum surface, which enables an AcTag to be seen by a camera. Detection through sound, on the other hand, is accomplished by the contrast of the scattering effects between rough and smooth surfaces. The rough surface of the acoustic foam generates high intensity returns even when the AcTag is not perpendicular to the sound wave. However, the smooth aluminum surface only reflects high intensities when it is perpendicular to the sonar, thus producing regions of light and dark pixels in the sonar that allow the AcTag to be detected.

The [actag](https://bitbucket.org/frostlab/actag/src/master/) repository and [apriltag](https://github.com/AprilRobotics/apriltag) repository can be used to detect AcTags in a sonar and camera, respectively. To detect an AcTag in a sonar view, see [Detecting AcTags with a Sonar](#markdown-header-detecting-actags-with-a-sonar). To detect AcTags in a camera view, see [Detecting AcTags with a Camera](#markdown-header-detecting-actags-with-a-camera).


(markdown-header-detecting-actags-with-a-sonar)=
## Detecting AcTags with a Sonar

### Prerequisites

Ensure that you have installed and can use the AcTag library. If you have not already done so, then please refer to the [installation instructions](./quickstart.md#installation)

### Usage
Once an AcTag has been captured in a sonar image, you can use the {class}`AcTag <actag.AcTag>` class to detect it. The {meth}{meth}`run_detection <actag.AcTag.run_detection>` method takes a sonar image as input, and returns a list of all the detected tags. For each tag, the tag id, corner indices, and corner range and azimuth values will be returned. Follow the steps below to use the {class}`AcTag <actag.AcTag>` class:

1. Import the {class}`AcTag <actag.AcTag>` class:
```python
from actag import AcTag
```

2. Initialize an AcTag object. See the {class}`AcTag <actag.AcTag>` class for information on the parameters. For example: 
```python
actagDetector = AcTag(min_range=0.1, max_range=1.5, horizontal_aperture=1.0472, 
                      vertical_aperture=0.20944, tag_family="AcTag24h10", 
                      tag_size=0.130628571428644)
```

*NOTE: If you are using an AcTag family that you generated yourself, you will need to pass the path to the AcTag family file in the ```tag_family``` parameter instead of the AcTag family name. For example:*
```python 
tag_family="/home/user/actag/actag_families/generated_families/AcTag24h4.java"
```

3. Import the sonar image.
```python
my_sonar_image = cv2.imread("exampleSonarImage.png")
```

4. Call {meth}`run_detection <actag.AcTag.run_detection>` with the sonar image. For example: 
```python
detected_tags = detector.run_detection(my_sonar_image)
```
Note that the sonar image should be a 2D numpy array with the format: 
```
[[(0, 0),  ...,  (0, -1)],        [[(max_range, max_azimuth), ..., (max_range, min_azimuth)],
[    ...,  ...,    ...  ],   ->    [         ...,             ...,            ...,         ],
[(-1, 0),  ..., (-1, -1)]]         [(min_range, max_azimuth), ..., (min_range, min_azimuth)]]
```
You can also run the detection algorithm with a visualization of each step using {meth}`visualize_detection <actag.AcTag.visualize_detection>`. For example:
```python
detected_tags = detector.visualize_detection(my_sonar_image)
```

5. Parse the results.  ```detected_tags``` will be a list of each of the detected tags. Each detected tag is a list of the form ```[tag_id, corner_indices, range_and_azimuth_values]```. ```tag_id``` is an integer value indicating the tag ID in the specified tag family. ```corner_indices``` is a 2D numpy array containing ```[row, column]``` pairs for each of the four corners of the tag. The top-left tag corner is first, followed by the top-right, and around in a clockwise fashion. Note that "top-left" refers to the corner in the top-left of the AcTag's image file, not the corner which happens to appear in the top-left of the current sonar image. ```range_and_azimuth_values``` is a 2D numpy array with ```[range, azimuth]``` pairs (in meters and radians, respectively) corresponding to each of the four corners, in the same order as ```corner_indices```.

### Example Scripts

#### Quickstart

<img src="../../actag_families/image_files/example_images/ExampleSonarImageDetected.png" alt="Example Sonar Image with the AcTag corners shown." width="400px">

A basic example of AcTag detection can be found on the [Quickstart](./quickstart.md) page. It demonstrates how to use the {class}`AcTag <actag.AcTag>` class, parse the results, and plot the information on the original image.

#### Video Detection

<img src="../../actag_families/image_files/example_images/AcTagDetection.gif"  alt="Video feed of an AcTag detected by a sonar." width="400px">

The [detect_actag_video.py](https://bitbucket.org/frostlab/actag/src/master/example_scripts/detect_actag_video.py) script in the [example_scripts](https://bitbucket.org/frostlab/actag/src/master/example_scripts/) folder is similar to the [Quickstart](#quickstart) example above, but expands upon it to use OpenCV's [VideoCapture](https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html) class for continuous detection on a video feed.

#### Polar Plotting

<img src="../../actag_families/image_files/example_images/ResultImage.png"  alt="AcTag detected by a sonar." width="400px">

The [detect_actag_polar_plotting.py](https://bitbucket.org/frostlab/actag/src/master/example_scripts/detect_actag_polar_plotting.py) script in the [example_scripts](https://bitbucket.org/frostlab/actag/src/master/example_scripts/) folder is similar to the [Quickstart](#quickstart) example above, but plots the sonar image in a polar coordinate system instead of cartesian. It also uses the calculated range and azimuth values to plot the tag corners onto the image, instead of the pixel locations of the corners.

(markdown-header-detecting-actags-with-a-camera)=
## Detecting AcTags with a Camera

### Setup

To detect an AcTag within a camera view, you'll first need to import your AcTag family into the [apriltag](https://github.com/AprilRobotics/apriltag) repository:

1. Download the [apriltag](https://github.com/AprilRobotics/apriltag) repository and follow the installation/build instructions found in the [README.md](https://github.com/AprilRobotics/apriltag/blob/master/README.md). NOTE: You may need to add ```sudo``` to some of the commands in order for them to work.
2. Find the C files generated for your AcTag family. These are located in the [actag_files_for_apriltag](https://bitbucket.org/frostlab/actag/src/master/actag_families/actag_files_for_apriltag/) directory under a folder with your family's name.
3. Copy the .c and .h files and save them in the main directory of the [apriltag](https://github.com/AprilRobotics/apriltag) repository.
4. Find the [apriltag_pywrap.c](https://github.com/AprilRobotics/apriltag/blob/master/apriltag_pywrap.c) file in the [apriltag](https://github.com/AprilRobotics/apriltag) repository, and open it.
5. Add an include statement for the .h file you just copied into the [apriltag](https://github.com/AprilRobotics/apriltag) repository. For example, if my tag family's name was "AcTag24h10", my .h file would be named "tagAcTag24h10.h", and I would include the following line into the [apriltag_pywrap.c](https://github.com/AprilRobotics/apriltag/blob/master/apriltag_pywrap.c) file:

```c
#include "tagAcTag24h10.h"
```

6. Find the following #define statement in the [apriltag_pywrap.c](https://github.com/AprilRobotics/apriltag/blob/master/apriltag_pywrap.c) file:

```c
#define SUPPORTED_TAG_FAMILIES(_)
    _(tag9h2)                               \
    _(tag36h10)                             \
    _(tag36h11)                             \
    ...
```

7. Append a line with your tag family's name onto the end of this define. For example, if my tag family's name was ``AcTag24h10``, I would append the following line onto the end of the define:

```c
    _(AcTag24h10)                           \
```

8. Rebuild the [apriltag](https://github.com/AprilRobotics/apriltag) repository with the instructions found in their [README.md](https://github.com/AprilRobotics/apriltag/blob/master/README.md).

Now that your AcTag family is imported into the [apriltag](https://github.com/AprilRobotics/apriltag) repository, you are ready to detect AcTags with the ```apriltag``` class.

### Usage

The ```apriltag``` class can be used to detect AcTags as AprilTags. The ```detect``` method takes a camera image as input, and returns a list of all the detected tags. Follow the steps below to use the ```apriltag``` class:

1. Import the ```apriltag``` class:
```python
from apriltag import apriltag
```

2. Initalize the ```apriltag``` class with the AcTag family name:
```python
detector = apriltag("AcTag24h10")
```

3. Import your AcTag image in greyscale, and invert the colors so that it becomes a valid AprilTag:
```python
import cv2
import numpy as np

image = cv2.imread("exampleCameraImage.png", cv2.IMREAD_COLOR)
imageGrey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
imageInv = np.invert(imageGrey)
```

4. Run the ```detect``` method on the color-inverted image:
```python
detected_tags = detector.detect(imageInv)
```
*NOTE: If you want to extract the AcTag's pose, you'll need to pass some additional parameters to the ```detect``` method. See the links below for more information.*

5. Parse the results. ```detected_tags``` will be a list of tags, with each tag as a dictionary. Each tag dictionary will contain the tag ID (```id```), the center coordinates in pixel space (```center```), the locations of the four corners in pixel space (```lb-rb-rt-lt```), the margin (```margin```), and the hamming distance of the detected data bits from the decoded tag (```hamming```). *Note that the ```lb-rb-rt-lt``` variable orders the corners by starting with the left-bottom corner, and going around the edge of the tag counter-clockwise. This is different than what the {meth}`AcTag.run_detection <actag.AcTag.run_detection>` method returns: the corners are ordered starting with the left-top corner, and going around the edge of the tag clockwise.* If you also enable pose detection with the ```detect``` method, there will be additional results with pose information. For more information on these values, see the links below.

For more information on using the ```apriltag``` class to detect AprilTags, see the [AprilTag User Guide](https://github.com/AprilRobotics/apriltag/wiki/AprilTag-User-Guide#python). You may also consider referring to the alternative library of Python bindings for AprilTag called [lib-dt-apriltags](https://github.com/duckietown/lib-dt-apriltags). While the Python bindings in this library are not an exact match with AprilTag, they exhibit a close resemblance. Therefore, consulting the documentation of [lib-dt-apriltags](https://github.com/duckietown/lib-dt-apriltags) can prove useful.

### Example Script

<img src="../../actag_families/image_files/example_images/AcTagCameraDetection.png"  alt="AcTag detected in a camera with the AprilTag library" width="400px">

The [detect_actag_with_apriltag.py](https://bitbucket.org/frostlab/actag/src/master/example_scripts/detect_actag_with_apriltag.py) script in the [example_scripts](https://bitbucket.org/frostlab/actag/src/master/example_scripts/) folder gives an example of how to use the ```apriltag``` class to detect an AcTag in Python. It also demonstrates how to parse the results and plot the information on the original image.