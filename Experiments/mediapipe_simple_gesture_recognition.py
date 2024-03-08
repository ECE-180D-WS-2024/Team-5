"""
Important: mp_pose.Pose() only seems to runs on MacOS using Python 3.9 and below
"""

import cv2
import mediapipe as mp

# Initialize MediaPipe Pose solution.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Helper function to check if a punch gesture is detected.
def is_punch(landmarks, image_height, image_width):
    # Right punch detection.
    right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
    right_punch = right_wrist.x > right_elbow.x + 0.1
    
    # Left punch detection (similar logic to right punch).
    left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    left_punch = left_wrist.x < left_elbow.x - 0.1  # Note the direction of comparison for left side.
    
    return right_punch or left_punch

# Capture video from the webcam.
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Convert the BGR image to RGB, and process it with MediaPipe Pose.
    image_height, image_width, _ = image.shape
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)

    # Draw the pose annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Check for punch gesture.
        if is_punch(results.pose_landmarks, image_height, image_width):
            cv2.putText(image, "PUNCH!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        # # Check for duck gesture.
        # if is_duck(results.pose_landmarks, image_height, image_width):
        #     cv2.putText(image, "DUCK!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('MediaPipe Pose with Gesture Recognition', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
