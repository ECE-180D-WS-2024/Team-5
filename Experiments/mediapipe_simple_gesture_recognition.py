"""
Important: mp_pose.Pose() only seems to runs on MacOS using Python 3.9 and below
"""

import cv2
import mediapipe as mp
import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address and port
server_address = ('127.0.0.1', 5000) # Example port, change as needed

# Message to send
message = 'Hello, Unity!'

try:
    # Send data
    print(f"Sending: {message}")
    sent = sock.sendto(message.encode(), server_address)
except Exception as e:
    print(e)

# Initialize MediaPipe Pose solution.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils


# Helper function to check if a punch gesture is detected.
def is_punch(landmarks):
    # Right punch detection.
    right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
    right_punch = right_wrist.x > right_elbow.x + 0.1

    # Left punch detection (similar logic to right punch).
    left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    left_punch = (
        left_wrist.x < left_elbow.x - 0.1
    )  # Note the direction of comparison for left side.

    return right_punch or left_punch


def is_block(landmarks):
    right_hand = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_hand = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    head_top = landmarks.landmark[
        mp_pose.PoseLandmark.NOSE
    ]  # Can use NOSE as a proxy for the head's top position.

    block = right_hand.y < head_top.y and left_hand.y < head_top.y
    return block


def is_duck(landmarks):
    nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
    shoulders_midpoint_y = (
        landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        + landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y
    ) / 2

    # Assuming a threshold for ducking (this might need adjustment).
    duck = nose.y > shoulders_midpoint_y + 0.1
    return duck


def is_kick(landmarks):
    # Access landmarks for knees and ankles.
    right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
    left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

    # Kick detection logic.
    # Assumes a kick when the ankle is significantly higher than the knee.
    # The threshold for detection (e.g., 0.1 here) might need to be adjusted based on actual use cases.
    right_kick = right_ankle.y < right_knee.y - 0.1  # Adjust the threshold as needed.
    left_kick = left_ankle.y < left_knee.y - 0.1  # Adjust the threshold as needed.

    return right_kick or left_kick


# Capture video from the webcam.
cap = cv2.VideoCapture(0)
last_move = ""
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
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

        # Check for punch gesture.
        if is_punch(results.pose_landmarks):
            cv2.putText(
                image,
                "PUNCH!",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            if last_move != "Punch":
                last_move = "Punch"
                message = "Punch"
                try:
                    # Send data
                    print(f"Sending: {message}")
                    sent = sock.sendto(message.encode(), server_address)
                except Exception as e:
                    print(e)

        if is_kick(results.pose_landmarks):
            cv2.putText(
                image,
                "KICK!",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
                cv2.LINE_AA,
            )

        if is_duck(results.pose_landmarks):
            cv2.putText(
                image,
                "DUCK!",
                (50, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        if is_block(results.pose_landmarks):
            cv2.putText(
                image,
                "BLOCK!",
                (50, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 128, 128),
                2,
                cv2.LINE_AA,
            )
            if last_move != "Block":
                last_move = "Block"
                message = "Block"
                try:
                    # Send data
                    print(f"Sending: {message}")
                    sent = sock.sendto(message.encode(), server_address)
                except Exception as e:
                    print(e)
            

    cv2.imshow("MediaPipe Pose with Gesture Recognition", image)
    if cv2.waitKey(5) & 0xFF == 27:
        sock.close()
        break

cap.release()
