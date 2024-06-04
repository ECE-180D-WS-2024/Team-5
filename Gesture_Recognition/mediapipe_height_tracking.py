import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6)
mp_drawing = mp.solutions.drawing_utils  # Drawing utilities

def get_player_height(image, results):
    height, width, _ = image.shape
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        head = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_heel = landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value]
        right_heel = landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value]

        # Ensure visibility of critical points
        if head.visibility < 0.6 or left_heel.visibility < 0.6 or right_heel.visibility < 0.6:
            return None, f"Player not fully visible. head: {head.visibility}, left_heel: {left_heel.visibility} right_heel:{right_heel.visibility}"

        # Get the lowermost heel
        foot_y = max(left_heel.y, right_heel.y)
        
        # Calculate fractional height
        player_height = abs(head.y - foot_y)
        return player_height, None
    return None, "Player not detected."

# Camera setup
cap = cv2.VideoCapture(0)  # Adjust the device index based on your camera setup
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        # Quit Process As Needed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        height_in_pixels, message = get_player_height(frame, results)
        if message:
            print(message)  # Broadcast message or handle it as needed
        elif height_in_pixels:
            print(f"Fractional player height: {height_in_pixels}")

        # Draw landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        time.sleep(1)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()