import cv2
import mediapipe as mp
import socket
import platform
from multiprocessing import Process

# Initialize MediaPipe Pose solution.
min_confidence = 0.6
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=min_confidence)
mp_drawing = mp.solutions.drawing_utils

# Helper function to check if a punch gesture is detected.
def is_punch(landmarks):
    # Right punch detection.
    right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]

    # Check if right wrist is above the right shoulder and in front of the right elbow
    right_punch = right_wrist.y < right_shoulder.y and right_wrist.x > right_elbow.x \
        and right_wrist.visibility > min_confidence\
        and right_shoulder.visibility > min_confidence\
        and right_elbow.visibility > min_confidence

    # Left punch detection (similar logic to right punch, but mirrored for left side).
    left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]

    # For the left side, check if left wrist is above the left shoulder and in front of the left elbow
    left_punch = left_wrist.y < left_shoulder.y and left_wrist.x < left_elbow.x\
        and left_wrist.visibility > min_confidence\
        and left_shoulder.visibility > min_confidence\
        and left_elbow.visibility > min_confidence

    # Using XOR to return True if either, but not both, punches are detected
    return right_punch ^ left_punch


def is_block(landmarks):
    right_hand = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_hand = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    head_top = landmarks.landmark[
        mp_pose.PoseLandmark.NOSE
    ]  # Can use NOSE as a proxy for the head's top position.
    block = right_hand.y < head_top.y and left_hand.y < head_top.y\
        and right_hand.visibility > min_confidence\
        and left_hand.visibility > min_confidence\
        and head_top.visibility > min_confidence
    
    return block


def is_kick(landmarks):
    # Access landmarks for knees and ankles.
    right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
    left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
    # Kick detection logic.
    # Assumes a kick when the ankle is close to the knee.
    # The threshold for detection (e.g., 0.1 here) might need to be adjusted based on actual use cases.
    right_kick = right_ankle.y < right_knee.y + 0.1\
        and right_ankle.visibility > min_confidence\
        and right_knee.visibility > min_confidence
    
    left_kick = left_ankle.y < left_knee.y + 0.1\
        and left_knee.visibility > min_confidence\
        and left_ankle.visibility > min_confidence
    
    return right_kick or left_kick

def send_message(player, server_address, message):
    message = f"{player}-{message}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        print(f"Sending: {message}")
        sent = sock.sendto(message.encode(), server_address)
    finally:
        sock.close()

def check_gestures(results):
    punch = is_punch(results.pose_landmarks)
    kick = is_kick(results.pose_landmarks)
    block = is_block(results.pose_landmarks)
    return punch, kick, block

def player_process(player, cam_no, port):
    server_address = ("127.0.0.1", port)
    cap = cv2.VideoCapture(cam_no)

    last_move = None
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # Quit Process As Needed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        # Process image with MediaPipe Pose
        image_height, image_width, _ = image.shape
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            punch, kick, block = check_gestures(results)

            if punch and last_move != "Punch":
                last_move = "Punch"
                send_message(player, server_address, "Punch")
            elif kick and last_move != "Kick":
                last_move = "Kick"
                send_message(player, server_address, "Kick")
            elif block and last_move != "Block":
                last_move = "Block"
                send_message(player, server_address, "Block")
            elif not any([punch, kick, block]) and last_move != "IDLE":
                last_move = "IDLE"
                send_message(player, server_address, "IDLE")

        cv2.imshow(f"MediaPipe Pose with Gesture Recognition - {player}", image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    system = platform.system()
    if system == 'Darwin':  # macOS
        cam_numbers = [0, 1]
    elif system == 'Windows':
        cam_numbers = [0, 1]
    else:
        cam_numbers = [0, 1]  # Default for other OS

    p1 = Process(target=player_process, args=('p1', cam_numbers[0], 5000))
    # p2 = Process(target=player_process, args=('p2', cam_numbers[1], 5000))
    p1.start()
    # p2.start()
    p1.join()
    # p2.join()
