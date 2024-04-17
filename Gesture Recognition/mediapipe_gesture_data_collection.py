import cv2
import mediapipe as mp
import os
import time

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

        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            # Get the label for the landmark
            landmark_label = mp_pose.PoseLandmark(idx).name
            print(f'{landmark_label} | x: {landmark.x}, y: {landmark.y}, z: {landmark.z}')
            if hasattr(landmark, 'visibility'):
                print(f'  - visibility: {landmark.visibility}')
            print()  # Empty line for better readability

    # Display the annotated frame
    cv2.imshow('Pose', frame)

    # time.sleep(0.1)  # Refresh rate (you can adjust this as needed)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
