import cv2
import mediapipe as mp
import socket
import platform
from multiprocessing import Process

# Mediapipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def get_player_height(results):
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        head = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_heel = landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value]
        right_heel = landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value]

        # Ensure visibility of critical points
        if head.visibility < 0.6 or left_heel.visibility < 0.6\
            or right_heel.visibility < 0.6:
            return None, "Player not fully visible."

        # Get the lowermost heel
        foot_y = max(left_heel.y, right_heel.y)

        # Calculate fractional height
        player_height = abs(head.y - foot_y)
        return player_height, None
    return None, "Player not detected."

def send_udp_packet(command, process_name, port):
    message = f"{process_name}-Move{command}"
    ip_address = "127.0.0.1"  # Localhost; replace with target IP if needed
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip_address, port))
    print(f"Sent command: {message} to {ip_address}:{port}")
    sock.close()

def camera_process(cam_no, port, process_name):
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6)
    cap = cv2.VideoCapture(cam_no)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue
            
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            player_height, error_message = get_player_height(results)
            
            if error_message:
                print(process_name + ": " + error_message)
                send_udp_packet("Error", process_name, port)
            elif player_height:
                # Determine movement command based on height
                if player_height > 0.7:
                    send_udp_packet("Forward", process_name, port)
                elif player_height < 0.55:
                    send_udp_packet("Backward", process_name, port)
                else:
                    send_udp_packet("Still", process_name, port)

                print(f"{process_name} player height: {player_height}")

            # Draw landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow(f'Frame - {process_name}', frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    system = platform.system()
    if system == 'Darwin':  # macOS
        cam_numbers = [0, 1]
    elif system == 'Windows':
        cam_numbers = [1, 2]
    else:
        cam_numbers = [0, 1]  # Default to Unix/Linux settings

    p1 = Process(target=camera_process, args=(cam_numbers[0], 5000, 'p1'))
    p2 = Process(target=camera_process, args=(cam_numbers[1], 6000, 'p2'))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
