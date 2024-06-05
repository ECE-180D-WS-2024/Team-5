import cv2
import mediapipe as mp
import pandas as pd
import os

# Initialize MediaPipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Open the video file
cap = cv2.VideoCapture('gayley_patrick.mp4')

# Define output data files
output_files = {
    '1': 'data/punch.csv',
    '2': 'data/kick.csv',
    '3': 'data/block.csv',
    '4': 'data/idle.csv'
}

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Function to save landmarks to CSV
def save_landmarks(landmarks, action):
    data = []
    for landmark in landmarks.landmark:
        data.extend([round(landmark.x, 4), round(landmark.y, 4), round(landmark.z, 4), round(landmark.visibility, 4)])
    
    columns = []
    for i in range(len(landmarks.landmark)):
        columns.extend([f'x_{i}', f'y_{i}', f'z_{i}', f'visibility_{i}'])

    df = pd.DataFrame([data], columns=columns)
    
    if not os.path.isfile(output_files[action]):
        df.to_csv(output_files[action], mode='a', header=True, index=False)
    else:
        df.to_csv(output_files[action], mode='a', header=False, index=False)

# Function to remove the last line from the CSV file
def remove_last_line(action):
    file_path = output_files[action]
    df = pd.read_csv(file_path)
    df = df[:-1]
    df.to_csv(file_path, index=False)

# Store all frames for easy access
frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Get frame dimensions
    height, width, _ = frame.shape
    
    # Calculate the width to be half of the height
    new_width = height * 2 // 3
    start_x = (width - new_width) // 2
    end_x = start_x + new_width
    
    # Crop the frame to the calculated dimensions
    cropped_frame = frame[:, start_x:end_x]
    
    frames.append(cropped_frame)

cap.release()

# To be able to rewind
action_history = []
current_frame_index = 0

while current_frame_index < len(frames):
    frame = frames[current_frame_index]

    # Convert the frame to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    
    # Process the image to extract pose landmarks
    results = pose.process(image)
    
    # Convert back to BGR for rendering
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Skip frame if no landmarks found
    if not results.pose_landmarks:
        current_frame_index += 1
        continue
    
    # Draw the pose annotation on the image
    mp.solutions.drawing_utils.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    # Display the image
    cv2.imshow('Frame', image)
    
    # Wait for user input to label the frame
    key = cv2.waitKey(0) & 0xFF
    
    if key == ord('q'):
        break
    elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
        save_landmarks(results.pose_landmarks, chr(key))
        action_history.append((chr(key), current_frame_index))
        current_frame_index += 1
    elif key == ord('r') and action_history:
        last_action, last_frame_index = action_history.pop()
        remove_last_line(last_action)
        current_frame_index = last_frame_index
    elif key == ord('0'):
        current_frame_index += 1
        continue

cv2.destroyAllWindows()
