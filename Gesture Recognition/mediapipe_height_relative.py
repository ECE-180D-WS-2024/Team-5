import cv2
import mediapipe as mp
import time
import socket

# Mediapipe setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6)
mp_drawing = mp.solutions.drawing_utils

def get_player_height(image, results):
    height, width, _ = image.shape
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        head = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_heel = landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value]
        right_heel = landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value]

        # Ensure visibility of critical points
        if head.visibility < 0.6 or left_heel.visibility < 0.6 or right_heel.visibility < 0.6:
            return None, "Player not fully visible."

        # Get the lowermost heel
        foot_y = max(left_heel.y, right_heel.y)

        # Calculate fractional height
        player_height = abs(head.y - foot_y)
        return player_height, None
    return None, "Player not detected."

# Function to send a UDP packet
def send_udp_packet(command):
    message = f"p1-Move{command}"
    port = 5000  # Static port assignment for demonstration
    ip_address = "127.0.0.1"  # Localhost; replace with target IP if needed
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip_address, port))
    print(f"Sent command: {message} to {ip_address}:{port}")
    sock.close()

# Camera setup
cap = cv2.VideoCapture(0)
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        player_height, message = get_player_height(frame, results)
        
        if message:
            print(message)
        elif player_height:
            # Determine movement command based on height
            if player_height > 0.65:
                send_udp_packet("Forward")
            elif player_height < 0.55:
                send_udp_packet("Backward")
            else:
                send_udp_packet("Still")

            print(f"Fractional player height: {player_height}")

        # Draw landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()