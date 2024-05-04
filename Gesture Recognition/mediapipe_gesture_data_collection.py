import cv2
import mediapipe as mp
import os

# Initialize MediaPipe Pose and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Start capturing video
cap = cv2.VideoCapture(0)

# Define a function to clear the screen
def clear_screen():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For Mac and Linux (os.name == 'posix')
    else:
        _ = os.system('clear')

# Landmark indices
LEFT_SHOULDER_INDEX = mp_pose.PoseLandmark.LEFT_SHOULDER.value
RIGHT_SHOULDER_INDEX = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
LEFT_HIP_INDEX = mp_pose.PoseLandmark.LEFT_HIP.value
RIGHT_HIP_INDEX = mp_pose.PoseLandmark.RIGHT_HIP.value

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame for pose landmarks
    results = pose.process(frame_rgb)

    # Clear the terminal screen
    clear_screen()

    # Draw pose landmarks on the frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        landmarks = results.pose_landmarks.landmark
        
        # Access and print selected landmarks directly
        shoulders_and_hips = [
            (LEFT_SHOULDER_INDEX, "LEFT_SHOULDER"),
            (RIGHT_SHOULDER_INDEX, "RIGHT_SHOULDER"),
            (LEFT_HIP_INDEX, "LEFT_HIP"),
            (RIGHT_HIP_INDEX, "RIGHT_HIP")
        ]

        z_pos = 0

        for idx, label in shoulders_and_hips:
            landmark = landmarks[idx]
            if landmark.visibility > 0.8:
                print(f'{label} | x: {landmark.x:.4f}, y: {landmark.y:.4f}, z: {landmark.z:.4f}, visibility: {landmark.visibility:.2f}')
                z_pos += landmark.z

        print(f"Final z position: {z_pos}")
        print(f'Position to send: {z_pos // 0.05}')

    # Display the annotated frame
    cv2.imshow('Pose', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
