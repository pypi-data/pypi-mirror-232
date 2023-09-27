import sys
import cv2
import numpy as np

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

# This helper function draws the detected tags onto the image
def visualize_decoded_tags(my_sonar_image, detected_tags):

    output_image = cv2.cvtColor(my_sonar_image, cv2.COLOR_GRAY2RGB)
    for detected_tag in detected_tags:
        # Extract corner points
        corner_locs = detected_tag[1]
        ptA = (corner_locs[0][0], corner_locs[0][1])
        ptB = (corner_locs[1][0], corner_locs[1][1])
        ptC = (corner_locs[2][0], corner_locs[2][1])
        ptD = (corner_locs[3][0], corner_locs[3][1])

        # Reverse x and y to get the correct orientation with cv2.imshow()
        ptA = (ptA[1], ptA[0])
        ptB = (ptB[1], ptB[0])
        ptC = (ptC[1], ptC[0])
        ptD = (ptD[1], ptD[0])

        # Draw the bounding box of the AcTag Square
        color = (0, 255, 0)
        cv2.line(output_image, ptA, ptB, color, 1)
        cv2.putText(output_image, "1", ptA, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.line(output_image, ptB, ptC, color, 1)
        cv2.putText(output_image, "2", ptB, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.line(output_image, ptC, ptD, color, 1)
        cv2.putText(output_image, "3", ptC, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.line(output_image, ptD, ptA, color, 1)
        cv2.putText(output_image, "4", ptD, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Put the Tag ID in the center
        center = (int((ptA[0] + ptC[0]) / 2), int((ptA[1] + ptC[1]) / 2))
        cv2.putText(output_image, "#" + str(detected_tag[0]), center,
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
    return output_image

# Demonstrates the use of the AcTag class
def main():

    # Initialize the AcTag Detector
    detector = AcTag(min_range=0.1, max_range=1.5, horizontal_aperture=1.0472, tag_family="AcTag24h10", 
                     tag_size=0.130628571428644, quads_use_same_random_vals=True)

    # Load the video
    video_file = "exampleSonarVideo.mp4"
    video_file_path = path_to_actag_detection + path_char + "example_scripts" + path_char + video_file
    cap = cv2.VideoCapture(video_file_path)

    # Check if camera opened successfully
    if (cap.isOpened() == False): 
        raise ValueError(f"Error opening video stream or file: {video_file_path}")
    
    # Read until video is completed
    while True:
        # Get the next frame
        ret, frame = cap.read()

        if ret == True:
            # Convert it to greyscale
            my_sonar_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            print(my_sonar_image.shape)

            # Detect tags in the image
            detected_tags = detector.run_detection(my_sonar_image)

            # Parse and print results
            parse_and_print_results(detected_tags)

            # Visualize decoded tags on the original image
            output_image = visualize_decoded_tags(my_sonar_image, detected_tags)
            cv2.imshow("Detected Tags", output_image)
        
            # Press Q on keyboard while the window is selected to exit
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        else: 
            break
    
    # When everything is done, release the video capture object
    cap.release()
    
    # Close all the OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()