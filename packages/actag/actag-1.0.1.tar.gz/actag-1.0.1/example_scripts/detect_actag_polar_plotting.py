import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt

path_to_actag_detection = __file__[:__file__.find("example_scripts")]
if '/' in path_to_actag_detection:
    path_char = '/'
else:
    path_char = '\\'
sys.path.append(path_to_actag_detection)

from actag import AcTag

# Helper function that parses AcTag detection data
# and prints the results
def parse_and_print_results(detected_tags):

    num_detected_tags = len(detected_tags)
    print("Number of Detected Tags: ", num_detected_tags)

    for i in range(0, len(detected_tags)):
        print("==== Tag #" + str(i) + " ====")
        detected_tag = detected_tags[i]
        print("Tag ID: ", detected_tag[0])
        print("Corner Locations: \n", detected_tag[1])
        print("Corner Range & Azimuth Locations: \n", detected_tag[2])

# Create a polar plot for an image with a specified field of view
# and minimum and maximum range. Also plot the detected_tags.
#
# Args:
#    data: The image to plot
#    fov_degrees: The horizontal aperature of the sonar (in degrees)
#    min_range: The minimum range of the sonar (in meters)
#    max_range: The maximum range of the sonar (in meters)
#    detected_tags: The tag detection returns from the run_detection() method
#    title: The title of the plot
#    
def plot_tags_polar(data: np.ndarray, fov_degrees: float, min_range: float, max_range: float, detected_tags, title: str='') -> None:
    # Optimal tag corner text alignments (used for plotting later)
    corner_ha_alignments = ['left', 'left', 'right', 'right']
    corner_va_alignments = ['top', 'bottom', 'bottom', 'top']
    
    # Get theta and range values for the image
    min_theta, max_theta = np.array([-fov_degrees/2, fov_degrees/2])
    ranges = np.linspace(max_range, min_range, data.shape[0])
    thetas = np.deg2rad(np.linspace(max_theta, min_theta, data.shape[1]))

    # Create a meshgrid so we can plot the 2D function
    thetasMesh, rangesMesh = np.meshgrid(thetas, ranges)
    
    # Create polar plot and set image values.
    figp, axp = plt.subplots(subplot_kw=dict(projection='polar'))
    axp.pcolormesh(thetasMesh, rangesMesh, data, cmap='gray')

    # Adjust origin to be in the center of the image
    axp.set_theta_zero_location('N')

    # Set bounds for theta and range
    axp.set_thetamin(min_theta)
    axp.set_thetamax(max_theta)
    axp.set_rmax(max_range)

    # Set title and turn off the grid
    axp.set_title(title)
    axp.grid(False)

    # Plot each detected tag
    for tag in detected_tags:
        # Extract the range and azimuth corner array
        corners_range_azi = tag[2]

        # Extract the four range and azimuth values for each corner
        ptA = (corners_range_azi[0][0], corners_range_azi[0][1])
        ptB = (corners_range_azi[1][0], corners_range_azi[1][1])
        ptC = (corners_range_azi[2][0], corners_range_azi[2][1])
        ptD = (corners_range_azi[3][0], corners_range_azi[3][1])
        pts = [ptA, ptB, ptC, ptD]

        # Calculate the center of the tag in range and azimuth
        center = ((ptA[0] + ptC[0])/2, (ptA[1] + ptC[1])/2)

        # Plot the tag number
        tagStr = "#" + str(tag[0])
        axp.text(center[1], center[0], tagStr, color='lime', fontsize=10, ha='center', va='center')
        
        # Draw each of the four lines
        for i in range(0, len(pts)):
            # Take two points at a time
            firstPoint = pts[i]
            secondPoint = pts[(i+1)%4]

            # Convert the x and y values to range and azimuth, respectively
            range_points = [firstPoint[0], secondPoint[0]]
            theta_points = [firstPoint[1], secondPoint[1]]

            # Plot the resulting line on the polar plot
            axp.add_line(plt.Line2D(theta_points, range_points, color='lime', fillstyle='full'))

            # Plot the corner number for the first point
            axp.text(theta_points[0], range_points[0], str(i), color='lime', fontsize=10, 
                     ha = corner_ha_alignments[i], va=corner_va_alignments[i])

    # Return the resulting axes
    return axp

# Demonstrates polar plotting of sonar imagery and AcTag detections
def main():

    # Initialize the AcTag Detector
    detector = AcTag(min_range=0.1, max_range=1.5, horizontal_aperture=1.0472, tag_family="AcTag24h10", 
                     tag_size=0.130628571428644, quads_use_same_random_vals=True)

    # Define the path to the example image
    img_path = "exampleSonarImage.png"

    # Load the sonar image
    image = cv2.imread(img_path, cv2.IMREAD_COLOR)
    # image = cv2.flip(cv2.flip(image, 0), 1)

    # Convert to grayscale
    imageGrey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect tags in the image
    detected_tags = detector.run_detection(imageGrey)

    # Parse and print results
    parse_and_print_results(detected_tags)

    # Create the polar plot and draw the detected tags onto it
    polarPlot = plot_tags_polar(imageGrey, 60, 0.1, 1.5, detected_tags, title="Detected Tags")

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()