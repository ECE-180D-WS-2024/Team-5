import cv2
import mediapipe as mp
import socket
import threading
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description="Process player argument.")
parser.add_argument(
    "--player",
    type=str,
    choices=["p1", "p2"],
    required=True,
    help="Player identifier (p1 or p2)",
)
args = parser.parse_args()

# Now you can use args.player to access the "player" variable
player = args.player
print(f"Player set to: {player}")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if player == "p1":
    # Server address and port
    server_address = ("127.0.0.1", 5000)  # Example port, change as needed

else:
    # Server address and port
    server_address = ("127.0.0.1", 6000)  # Example port, change as needed


def send_message(message):
    message = f"{player}-{message}"
    try:
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
    right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]

    # Check if right wrist is above the right shoulder and in front of the right elbow
    right_punch = right_wrist.y < right_shoulder.y and right_wrist.x > right_elbow.x

    # Left punch detection (similar logic to right punch, but mirrored for left side).
    left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]

    # For the left side, check if left wrist is above the left shoulder and in front of the left elbow
    left_punch = left_wrist.y < left_shoulder.y and left_wrist.x < left_elbow.x

    # Using XOR to return True if either, but not both, punches are detected
    return right_punch ^ left_punch


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
    # Assumes a kick when the ankle is close to the knee.
    # The threshold for detection (e.g., 0.1 here) might need to be adjusted based on actual use cases.
    right_kick = right_ankle.y < right_knee.y + 0.1  # Adjust the threshold as needed.
    left_kick = left_ankle.y < left_knee.y + 0.1  # Adjust the threshold as needed.
    return right_kick or left_kick


# Capture video from the webcam.
if player == "p1":
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(1)
last_move = None
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
                threading.Thread(target=send_message, args=(message,)).start()

        elif is_kick(results.pose_landmarks):
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
            if last_move != "Kick":
                last_move = "Kick"
                message = "Kick"
                threading.Thread(target=send_message, args=(message,)).start()

        elif is_duck(results.pose_landmarks):
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
            if last_move != "Duck":
                last_move = "Duck"
                message = "Duck"
                threading.Thread(target=send_message, args=(message,)).start()

        elif is_block(results.pose_landmarks):
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
                threading.Thread(target=send_message, args=(message,)).start()

        else:
            cv2.putText(
                image,
                "IDLE",
                (50, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 128, 128),
                2,
                cv2.LINE_AA,
            )
            if last_move != "IDLE":
                last_move = "IDLE"
                message = "IDLE"
                threading.Thread(target=send_message, args=(message,)).start()

    cv2.imshow("MediaPipe Pose with Gesture Recognition", image)
    if cv2.waitKey(5) & 0xFF == 27:
        sock.close()
        break
cap.release()
