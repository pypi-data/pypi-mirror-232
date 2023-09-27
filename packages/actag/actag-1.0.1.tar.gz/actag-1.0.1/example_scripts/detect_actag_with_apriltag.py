import cv2
import sys
import numpy as np
from apriltag import apriltag

path_to_actag_detection = __file__[:__file__.find("example_scripts")]
sys.path.append(path_to_actag_detection)

# Demonstrates the use of the apriltag class
def main():
    img_path = "exampleCameraImage.png"

    # Load the image
    image = cv2.imread(img_path, cv2.IMREAD_COLOR)

    # Convert to grayscale
    imageGrey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Flip the image colors
    imageInv = np.invert(imageGrey)

    # Initialize the apriltag detector
    detector = apriltag("AcTag24h10")

    # Detect tags in the image
    detected_tags = detector.detect(imageInv)
    print(detected_tags)

    # Parse and print results
    num_detected_tags = len(detected_tags)
    print("Number of Detected Tags: ", num_detected_tags)

    for i in range(0, len(detected_tags)):
        print("==== Tag #" + str(i) + " ====")
        detected_tag = detected_tags[i]
        print("Tag ID: ", detected_tag['id'])
        print("Hamming: ", detected_tag['hamming'])
        print("Margin: ", detected_tag['margin'])
        print("Center of Tag: ", detected_tag['center'])
        print("Corner Locations (lb-rb-rt-lt): \n", detected_tag['lb-rb-rt-lt'])

    # Visualize decoded tags on the original image
    for detected_tag in detected_tags:
        # Extract corner points
        (ptD, ptC, ptB, ptA) = detected_tag['lb-rb-rt-lt']

        # Reverse x and y to get the correct orientation with cv2.imshow()
        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))
        ptA = (int(ptA[0]), int(ptA[1]))

        # Draw the bounding box of the AprilTag square
        color = (0, 255, 0)
        cv2.line(image, ptA, ptB, (0, 255, 0), 4)
        cv2.putText(image, "1", ptA, cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5)
        cv2.line(image, ptB, ptC, (0, 255, 0), 4)
        cv2.putText(image, "2", ptB, cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5)
        cv2.line(image, ptC, ptD, (0, 255, 0), 4)
        cv2.putText(image, "3", ptC, cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5)
        cv2.line(image, ptD, ptA, (0, 255, 0), 4)
        cv2.putText(image, "4", ptD, cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5)

        # Draw the center (x, y)-coordinates of the AprilTag
        (cX, cY) = (int(detected_tag['center'][0]), int(detected_tag['center'][1]))
        cv2.circle(image, (cX, cY), 5, (0, 255, 0), -1)

        # Put the Tag ID in the center
        tagID = "#" + str(detected_tag['id'])
        cv2.putText(image, tagID, (cX + 15, cY + 15),
            cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)

    # Scale the output image after AprilTag detection
    scalePercent = 30
    width = int(image.shape[1] * scalePercent / 100)
    height = int(image.shape[0] * scalePercent / 100)
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

    # Show the output image after AprilTag detection
    print("Displaying Detected Tags on original image. Press 'q' to quit.")
    cv2.imshow("Detected Tags", resized)
    while cv2.waitKey(0) != ord('q'):
        pass
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()