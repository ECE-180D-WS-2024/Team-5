import cv2
import numpy as np


def adjust_brightness_contrast(image, brightness=0, contrast=0):
    """
    Adjust the brightness and contrast of an image.
    :param image: Input image
    :param brightness: Brightness adjustment factor
    :param contrast: Contrast adjustment factor
    :return: The adjusted image
    """
    # Convert to float to prevent clipping and loss of info during transformation
    img_float = image.astype(float)

    # Apply brightness and contrast adjustments
    img_float = img_float * (contrast / 127 + 1) - contrast + brightness

    # Clip values to the valid range [0, 255] and convert back to uint8
    img_float = np.clip(img_float, 0, 255).astype(np.uint8)

    return img_float


# Open the webcam device
cap = cv2.VideoCapture(1)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Adjust the frame's brightness and contrast
    # You might need to tweak these values
    adjusted_frame = adjust_brightness_contrast(frame, brightness=-64, contrast=64)

    # Display the adjusted frame
    cv2.imshow("Adjusted Frame", adjusted_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the webcam and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
