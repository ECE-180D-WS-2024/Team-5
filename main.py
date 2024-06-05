import socket
import time
import asyncio
import cv2
import mediapipe as mp
from multiprocessing import Process
import platform
import localization
from localization import get_player_movement, get_player_height
from imu import init_imu, get_imu_val
from gesture import get_gesture
import threading
import select

LAST_MOVE = "MoveStill"
LAST_ACTION = "Idle"
GESTURE_TIMEOUT = 0.5  # 0.5 seconds timeout for gestures

# Dictionary to store the last sent time for each gesture
last_sent_times = {
    "Punch": 0,
    "Block": 0,
    "Kick": 0,
    # idle can be sent multiple times
}

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
    global LAST_ACTION
    # Recognize gesture
    gesture = get_gesture(landmarks)
    current_time = time.time()

    # Check if the gesture is in the timeout list and if the timeout has passed
    if gesture in last_sent_times and current_time - last_sent_times[gesture] < GESTURE_TIMEOUT:
        return

    # Update the last sent time for the gesture
    last_sent_times[gesture] = current_time
    if LAST_ACTION == gesture:
        return
    if gesture == "Punch" and get_imu_val()[0] > 0:
        gesture = f"StrongPunch{int(get_imu_val()[0])}"
    LAST_ACTION = gesture
    threading.Thread(target=send_message, args=(player, gesture)).start()

def get_and_send_movement(landmarks, player):
    global LAST_MOVE
    # Get player movement through localization
    movement = get_player_movement(player, landmarks)
    if LAST_MOVE == movement:
        return
    LAST_MOVE = movement
    threading.Thread(target=send_message, args=(player, movement)).start()

def receive_calibration_message(sock, timeout=1):
    ready = select.select([sock], [], [], timeout)
    if ready[0]:
        data, _ = sock.recvfrom(1024)
        print("Received data: ", data.decode())
        return data.decode()
    return None

def calibrate_player(player, cam_no, port=6000):
    cap = cv2.VideoCapture(cam_no)
    print(f"Calibrating {player}...")

    thresholds_set = {'ForwardThreshold': False, 'BackwardThreshold': False}
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', port))

    while not all(thresholds_set.values()):
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        height, width, _ = frame.shape
        new_width = height * 2 // 3
        start_x = (width - new_width) // 2
        end_x = start_x + new_width
        image = frame[:, start_x:end_x]

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            player_height, error_message = get_player_height(landmarks)
            if error_message:
                print(f"Error: {error_message}")
                continue

            calibration_message = receive_calibration_message(udp_sock)
            if calibration_message == f"{player}-ForwardThreshold":
                localization.forward_threshold[player] = player_height
                thresholds_set['ForwardThreshold'] = True
                print(f"{player} forward threshold set to {player_height}")
            elif calibration_message == f"{player}-BackwardThreshold":
                localization.backward_threshold[player] = player_height
                thresholds_set['BackwardThreshold'] = True
                print(f"{player} backward threshold set to {player_height}")

        cv2.imshow(f"Calibration - {player}", image)
        if cv2.waitKey(5) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Calibration complete for {player}.")

async def process_camera_feed(player, cam_no, port=6000):
    calibrate_player(player, cam_no, port)  # Calibrate player before starting main loop
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
            get_and_send_gesture(landmarks, player)
            get_and_send_movement(landmarks, player)

        cv2.imshow(f"Gesture - {player}", image)
        if cv2.waitKey(5) & 0xFF == ord("q"):
            break

        await asyncio.sleep(0)  # Yield control to the event loop

    cap.release()
    cv2.destroyAllWindows()

async def player_process(player, cam_no, port=5000):
    imu_task = asyncio.create_task(init_imu(player))
    camera_task = asyncio.create_task(process_camera_feed(player, cam_no, port))

    await asyncio.gather(imu_task, camera_task)

def run_player_process(player, cam_no, port=5000):
    asyncio.run(player_process(player, cam_no, port))

if __name__ == '__main__':
    system = platform.system()
    if system == 'Darwin':  # macOS
        cam_numbers = [0, 1]
    elif system == 'Windows':
        cam_numbers = [1, 2]
    else:
        cam_numbers = [0, 1]  # Default for other OS

    p1 = Process(target=run_player_process, args=('p1', cam_numbers[0], 6000))
    p2 = Process(target=run_player_process, args=('p2', cam_numbers[1], 6001))
    p1.start()
    p2.start()
    p1.join()
    p2.join()