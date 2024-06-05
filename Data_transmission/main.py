import socket
import asyncio
import cv2
import mediapipe as mp
from multiprocessing import Process
import platform
from localization import get_player_movement
from imu import init_imu, get_imu_val
from gesture import get_gesture
import concurrent.futures

LAST_MOVE = None
LAST_ACTION = None

# Create a thread pool with a maximum number of worker threads
max_workers = 8  # Adjust based on your requirements and system capabilities
executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

# Initialize MediaPipe Pose solution.
min_confidence = 0.8
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_tracking_confidence=min_confidence, min_detection_confidence=min_confidence)
mp_drawing = mp.solutions.drawing_utils

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_message(player, message, port=5000, server_address="127.0.0.1"):
    message = f"{player}-{message}"
    try:
        print(f"Sending: {message}")
        sent = sock.sendto(message.encode(), (server_address, port))
    except Exception as e:
        print(e)

def get_and_send_gesture(landmarks, player):
    # Recognize gesture
    gesture = get_gesture(landmarks)
    if LAST_ACTION == gesture:
        return
    if gesture == "Punch" and get_imu_val() > 0:
        gesture = f"StrongPunch{int(get_imu_val())}"
    LAST_ACTION = gesture
    send_message(player, gesture)

def get_and_send_movement(landmarks, player):
    # Get player movement through localization
    movement = get_player_movement(landmarks)
    if LAST_MOVE == movement:
        return
    LAST_MOVE = movement
    send_message(player, movement)

def player_process(player, cam_no, port=5000):
    # Start reading in IMU values
    asyncio.create_task(init_imu(player))
    cap = cv2.VideoCapture(cam_no)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Get frame dimensions
        height, width, _ = frame.shape
        
        # Calculate the width to be half of the height
        new_width = height * 2 // 3
        start_x = (width - new_width) // 2
        end_x = start_x + new_width
        
        # Crop the frame to the calculated dimensions
        image = frame[:, start_x:end_x]

        # Process image with MediaPipe Pose
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark
            # Submit tasks to the thread pool
            executor.submit(get_and_send_gesture, landmarks, player)
            executor.submit(get_and_send_movement, landmarks, player)

        cv2.imshow(f"MediaPipe Pose with Gesture Recognition - {player}", image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    executor.shutdown(wait=True)

if __name__ == '__main__':
    system = platform.system()
    if system == 'Darwin':  # macOS
        cam_numbers = [0, 1]
    elif system == 'Windows':
        cam_numbers = [1, 2]
    else:
        cam_numbers = [0, 1]  # Default for other OS

    p1 = Process(target=player_process, args=('p1', cam_numbers[0]))
    # p2 = Process(target=player_process, args=('p2', cam_numbers[1]))
    p1.start()
    # p2.start()
    p1.join()
    # p2.join()